import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Node {
  id: string;
  type: 'gene' | 'pathway';
  label: string;
}

interface Link {
  source: string;
  target: string;
}

const NetworkGraph = () => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 800;
    const height = 600;

    // Sample data
    const nodes: Node[] = [
      { id: 'p1', type: 'pathway', label: 'PI3K-AKT' },
      { id: 'p2', type: 'pathway', label: 'Cell Cycle' },
      { id: 'p3', type: 'pathway', label: 'p53' },
      { id: 'g1', type: 'gene', label: 'TP53' },
      { id: 'g2', type: 'gene', label: 'PIK3CA' },
      { id: 'g3', type: 'gene', label: 'BRCA1' },
      { id: 'g4', type: 'gene', label: 'CDK4' },
      { id: 'g5', type: 'gene', label: 'PTEN' },
    ];

    const links: Link[] = [
      { source: 'g1', target: 'p3' },
      { source: 'g2', target: 'p1' },
      { source: 'g3', target: 'p3' },
      { source: 'g4', target: 'p2' },
      { source: 'g5', target: 'p1' },
      { source: 'g2', target: 'g5' },
      { source: 'g1', target: 'g3' },
    ];

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    svg.attr('width', width).attr('height', height);

    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        'link',
        d3.forceLink(links).id((d: any) => d.id).distance(150)
      )
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#a855f7')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Draw nodes
    const node = svg
      .append('g')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .call(
        d3.drag<any, any>()
          .on('start', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d: any) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    node
      .append('circle')
      .attr('r', (d) => (d.type === 'pathway' ? 40 : 25))
      .attr('fill', (d) => (d.type === 'pathway' ? '#8b5cf6' : '#ec4899'))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    node
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', 4)
      .attr('fill', 'white')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('pointer-events', 'none');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });
  }, []);

  return (
    <div className="flex justify-center bg-white/5 rounded-lg">
      <svg ref={svgRef} />
    </div>
  );
};

export default NetworkGraph;
