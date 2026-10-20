/**
 * COINVAULT — Apache ECharts Financial Graphics Engine
 * Produces crisp sparklines, area gradients, and stat duel comparison charts.
 */

window.COINVAULT_CHARTS = (function () {
  'use strict';

  function isDarkTheme() {
    return document.documentElement.classList.contains('dark');
  }

  // 1. MINI SPARKLINES FOR LEADERBOARD ROWS
  function renderSparklines() {
    if (typeof echarts === 'undefined') return;

    const sparkEls = document.querySelectorAll('.cv-sparkline');
    sparkEls.forEach((el) => {
      const dataRaw = el.getAttribute('data-points');
      if (!dataRaw) return;

      try {
        const points = JSON.parse(dataRaw);
        if (!points || points.length < 2) return;

        // Dispose previous instance if already rendered
        const existing = echarts.getInstanceByDom(el);
        if (existing) existing.dispose();

        const chart = echarts.init(el, null, { renderer: 'svg' });
        const isUp = points[points.length - 1] >= points[0];
        const lineColor = isUp ? '#00F084' : '#FF3B56';

        const option = {
          animation: false,
          grid: { top: 2, bottom: 2, left: 2, right: 2 },
          xAxis: { type: 'category', show: false },
          yAxis: { type: 'value', show: false, min: 'dataMin', max: 'dataMax' },
          series: [
            {
              data: points,
              type: 'line',
              smooth: 0.3,
              showSymbol: false,
              lineStyle: { color: lineColor, width: 1.8 },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: isUp ? 'rgba(0, 240, 132, 0.25)' : 'rgba(255, 59, 86, 0.25)' },
                  { offset: 1, color: 'transparent' },
                ]),
              },
            },
          ],
        };
        chart.setOption(option);
      } catch (err) {
        console.error('Error rendering sparkline', err);
      }
    });
  }

  // 2. MAIN USER BALANCE TIME-SERIES CHART
  function renderUserHistoryChart(containerId, labels, values) {
    if (typeof echarts === 'undefined') return null;
    const el = document.getElementById(containerId);
    if (!el || !values || !values.length) return null;

    const existing = echarts.getInstanceByDom(el);
    if (existing) existing.dispose();

    const chart = echarts.init(el);
    const dark = isDarkTheme();

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: dark ? '#0F141C' : '#FFFFFF',
        borderColor: dark ? 'rgba(245, 196, 81, 0.4)' : 'rgba(217, 130, 20, 0.4)',
        borderWidth: 1,
        textStyle: {
          color: dark ? '#F1F5F9' : '#0F172A',
          fontFamily: 'JetBrains Mono',
          fontSize: 12,
        },
        formatter: function (params) {
          const p = params[0];
          return `
            <div style="font-family:Inter,sans-serif; font-size:11px; color:#94A3B8; margin-bottom:4px;">${p.name}</div>
            <div style="font-weight:700; color:#F5C451; font-size:14px;">
              ${Number(p.value).toLocaleString()} <span style="font-size:10px; color:#94A3B8;">coins</span>
            </div>
          `;
        },
      },
      grid: {
        top: 20,
        right: 20,
        bottom: 30,
        left: 55,
      },
      xAxis: {
        type: 'category',
        data: labels,
        boundaryGap: false,
        axisLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.1)' : 'rgba(15,23,42,0.1)' } },
        axisLabel: {
          color: dark ? '#64748B' : '#94A3B8',
          fontSize: 11,
          fontFamily: 'Inter',
        },
        splitLine: { show: false },
      },
      yAxis: {
        type: 'value',
        scale: true,
        axisLine: { show: false },
        axisLabel: {
          color: dark ? '#64748B' : '#94A3B8',
          fontSize: 11,
          fontFamily: 'JetBrains Mono',
          formatter: (v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v,
        },
        splitLine: {
          lineStyle: {
            color: dark ? 'rgba(255,255,255,0.05)' : 'rgba(15,23,42,0.05)',
            type: 'dashed',
          },
        },
      },
      series: [
        {
          name: 'Balance',
          type: 'line',
          smooth: 0.35,
          showSymbol: false,
          symbolSize: 6,
          data: values,
          itemStyle: { color: '#F5C451' },
          lineStyle: {
            width: 2.5,
            color: '#F5C451',
            shadowColor: 'rgba(245, 196, 81, 0.4)',
            shadowBlur: 10,
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(245, 196, 81, 0.35)' },
              { offset: 0.7, color: 'rgba(245, 196, 81, 0.05)' },
              { offset: 1, color: 'transparent' },
            ]),
          },
        },
      ],
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
    return chart;
  }

  // 3. COMPARE HEAD-TO-HEAD OVERLAY CHART
  function renderCompareChart(containerId, dates, user1Data, user2Data) {
    if (typeof echarts === 'undefined') return null;
    const el = document.getElementById(containerId);
    if (!el) return null;

    const existing = echarts.getInstanceByDom(el);
    if (existing) existing.dispose();

    const chart = echarts.init(el);
    const dark = isDarkTheme();

    const option = {
      backgroundColor: 'transparent',
      legend: {
        textStyle: { color: dark ? '#94A3B8' : '#475569', fontFamily: 'Inter' },
        top: 0,
        right: 10,
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: dark ? '#0F141C' : '#FFFFFF',
        borderColor: dark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(15, 23, 42, 0.15)',
        textStyle: { color: dark ? '#F1F5F9' : '#0F172A', fontFamily: 'JetBrains Mono' },
      },
      grid: { top: 40, right: 20, bottom: 30, left: 60 },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.1)' : 'rgba(15,23,42,0.1)' } },
        axisLabel: { color: dark ? '#64748B' : '#94A3B8', fontSize: 11 },
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.05)' : 'rgba(15,23,42,0.05)', type: 'dashed' } },
        axisLabel: {
          color: dark ? '#64748B' : '#94A3B8',
          fontFamily: 'JetBrains Mono',
          formatter: (v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v,
        },
      },
      series: [
        {
          name: user1Data.name,
          type: 'line',
          smooth: 0.3,
          data: user1Data.values,
          lineStyle: { width: 2.5, color: '#F5C451' },
          itemStyle: { color: '#F5C451' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(245, 196, 81, 0.25)' },
              { offset: 1, color: 'transparent' },
            ]),
          },
        },
        {
          name: user2Data.name,
          type: 'line',
          smooth: 0.3,
          data: user2Data.values,
          lineStyle: { width: 2.5, color: '#00D8F6' },
          itemStyle: { color: '#00D8F6' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 216, 246, 0.25)' },
              { offset: 1, color: 'transparent' },
            ]),
          },
        },
      ],
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
    return chart;
  }

  // 4. GLOBAL DISTRIBUTION HISTOGRAM
  function renderDistributionHistogram(containerId, brackets) {
    if (typeof echarts === 'undefined') return null;
    const el = document.getElementById(containerId);
    if (!el || !brackets || !brackets.length) return null;

    const existing = echarts.getInstanceByDom(el);
    if (existing) existing.dispose();

    const chart = echarts.init(el);
    const dark = isDarkTheme();

    const labels = brackets.map((b) => b.label);
    const counts = brackets.map((b) => b.count);

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: dark ? '#0F141C' : '#FFFFFF',
        borderColor: 'rgba(245, 196, 81, 0.3)',
        textStyle: { color: dark ? '#F1F5F9' : '#0F172A', fontFamily: 'Inter' },
        formatter: (params) => `${params[0].name}: <b>${params[0].value} players</b>`,
      },
      grid: { top: 20, right: 20, bottom: 30, left: 40 },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.1)' : 'rgba(15,23,42,0.1)' } },
        axisLabel: { color: dark ? '#94A3B8' : '#475569', fontSize: 11, fontFamily: 'JetBrains Mono' },
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.05)' : 'rgba(15,23,42,0.05)' } },
        axisLabel: { color: dark ? '#64748B' : '#94A3B8', fontFamily: 'JetBrains Mono' },
      },
      series: [
        {
          type: 'bar',
          data: counts,
          barWidth: '40%',
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#F5C451' },
              { offset: 1, color: '#C9961E' },
            ]),
          },
        },
      ],
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
    return chart;
  }

  // Auto-run sparklines on load
  document.addEventListener('DOMContentLoaded', renderSparklines);
  window.addEventListener('cv:themeChanged', renderSparklines);

  return {
    renderSparklines: renderSparklines,
    renderUserHistoryChart: renderUserHistoryChart,
    renderCompareChart: renderCompareChart,
    renderDistributionHistogram: renderDistributionHistogram,
  };
})();
