import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const VennDiagram = () => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 600;
    const height = 400;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 100;

    svg.attr('width', width).attr('height', height);

    // Create circles for each omics layer
    const circles = [
      { cx: centerX - 60, cy: centerY - 40, r: radius, color: '#8b5cf6', label: 'Expression', count: 145 },
      { cx: centerX + 60, cy: centerY - 40, r: radius, color: '#ec4899', label: 'Mutations', count: 87 },
      { cx: centerX, cy: centerY + 60, r: radius, color: '#06b6d4', label: 'Methylation', count: 112 },
    ];

    // Draw circles
    circles.forEach((circle) => {
      svg
        .append('circle')
        .attr('cx', circle.cx)
        .attr('cy', circle.cy)
        .attr('r', circle.r)
        .attr('fill', circle.color)
        .attr('fill-opacity', 0.3)
        .attr('stroke', circle.color)
        .attr('stroke-width', 2);

      // Add labels
      svg
        .append('text')
        .attr('x', circle.cx)
        .attr('y', circle.cy - radius - 10)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text(circle.label);

      // Add counts
      svg
        .append('text')
        .attr('x', circle.cx)
        .attr('y', circle.cy)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-size', '24px')
        .attr('font-weight', 'bold')
        .text(circle.count);
    });

    // Add intersection count (center)
    svg
      .append('text')
      .attr('x', centerX)
      .attr('y', centerY + 5)
      .attr('text-anchor', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '32px')
      .attr('font-weight', 'bold')
      .text('23');

    svg
      .append('text')
      .attr('x', centerX)
      .attr('y', centerY + 25)
      .attr('text-anchor', 'middle')
      .attr('fill', '#a855f7')
      .attr('font-size', '12px')
      .text('Multi-Omics Hits');
  }, []);

  return (
    <div className="flex justify-center">
      <svg ref={svgRef} />
    </div>
  );
};

export default VennDiagram;
