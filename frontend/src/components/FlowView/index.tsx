import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Card, Button, Space, Slider, Select } from 'antd'
import { PlayCircleOutlined, PauseCircleOutlined, FastForwardOutlined } from '@ant-design/icons'

interface FlowNode {
  id: string
  label: string
  type: 'start' | 'end' | 'condition' | 'action' | 'loop'
  line?: number
}

interface FlowEdge {
  source: string
  target: string
  label?: string
}

interface ControlFlowViewProps {
  projectId: string
  functionId?: string
  functionName?: string
  code?: string
  onNodeClick?: (nodeId: string, line: number) => void
}

export default function ControlFlowView({
  projectId,
  functionId,
  functionName,
  code,
  onNodeClick,
}: ControlFlowViewProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [currentStep, setCurrentStep] = useState(0)

  // 模拟控制流数据
  const mockFlowData: { nodes: FlowNode[]; edges: FlowEdge[] } = {
    nodes: [
      { id: 'start', label: '开始', type: 'start' },
      { id: 'validate', label: '参数校验', type: 'action', line: 10 },
      { id: 'check', label: '是否有效?', type: 'condition', line: 15 },
      { id: 'process', label: '业务处理', type: 'action', line: 20 },
      { id: 'loop', label: '循环处理', type: 'loop', line: 25 },
      { id: 'save', label: '保存数据', type: 'action', line: 30 },
      { id: 'return', label: '返回结果', type: 'end' },
      { id: 'error', label: '返回错误', type: 'end' },
    ],
    edges: [
      { source: 'start', target: 'validate' },
      { source: 'validate', target: 'check' },
      { source: 'check', target: 'process', label: '是' },
      { source: 'check', target: 'error', label: '否' },
      { source: 'process', target: 'loop' },
      { source: 'loop', target: 'save', label: '遍历' },
      { source: 'loop', target: 'return', label: '完成' },
      { source: 'save', target: 'loop' },
    ],
  }

  useEffect(() => {
    if (!svgRef.current) return

    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    // 清除现有内容
    svg.selectAll('*').remove()

    // 创建箭头标记
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .append('path')
      .attr('d', 'M 0,-5 L 10,0 L 0,5')
      .attr('fill', '#999')

    // 创建图形组
    const g = svg.append('g')

    // 节点颜色映射
    const nodeColors: Record<string, string> = {
      start: '#52c41a',
      end: '#ff4d4f',
      condition: '#faad14',
      action: '#1890ff',
      loop: '#722ed1',
    }

    // 节点位置（手动布局）
    const nodePositions: Record<string, { x: number; y: number }> = {
      start: { x: width / 2, y: 50 },
      validate: { x: width / 2, y: 120 },
      check: { x: width / 2, y: 200 },
      process: { x: width / 3, y: 280 },
      error: { x: 2 * width / 3, y: 280 },
      loop: { x: width / 3, y: 360 },
      save: { x: width / 3, y: 440 },
      return: { x: width / 2, y: 520 },
    }

    // 绘制边
    const edges = g
      .append('g')
      .attr('class', 'edges')
      .selectAll('path')
      .data(mockFlowData.edges)
      .enter()
      .append('path')
      .attr('d', (d) => {
        const source = nodePositions[d.source]
        const target = nodePositions[d.target]
        return `M ${source.x} ${source.y + 25} Q ${source.x} ${(source.y + target.y) / 2} ${(source.x + target.x) / 2} ${(source.y + target.y) / 2} T ${target.x} ${target.y - 25}`
      })
      .attr('fill', 'none')
      .attr('stroke', '#999')
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrowhead)')

    // 绘制边标签
    g.append('g')
      .attr('class', 'edge-labels')
      .selectAll('text')
      .data(mockFlowData.edges.filter((e) => e.label))
      .enter()
      .append('text')
      .text((d) => d.label || '')
      .attr('x', (d) => (nodePositions[d.source].x + nodePositions[d.target].x) / 2)
      .attr('y', (d) => (nodePositions[d.source].y + nodePositions[d.target].y) / 2 - 5)
      .attr('text-anchor', 'middle')
      .attr('font-size', 12)
      .attr('fill', '#666')
      .attr('background', 'white')

    // 绘制节点
    const nodeGroups = g
      .append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(mockFlowData.nodes)
      .enter()
      .append('g')
      .attr('transform', (d) => `translate(${nodePositions[d.id].x}, ${nodePositions[d.id].y})`)
      .style('cursor', 'pointer')
      .on('click', (_, d) => {
        if (d.line && onNodeClick) {
          onNodeClick(d.id, d.line)
        }
      })

    // 节点形状
    nodeGroups.each(function (d) {
      const node = d3.select(this)
      const color = nodeColors[d.type] || '#1890ff'

      if (d.type === 'start' || d.type === 'end') {
        // 圆角矩形
        node
          .append('rect')
          .attr('x', -40)
          .attr('y', -15)
          .attr('width', 80)
          .attr('height', 30)
          .attr('rx', 15)
          .attr('fill', color)
      } else if (d.type === 'condition') {
        // 菱形
        node
          .append('polygon')
          .attr('points', '0,-25 50,0 0,25 -50,0')
          .attr('fill', color)
      } else if (d.type === 'loop') {
        // 六边形
        node
          .append('polygon')
          .attr('points', '-30,-15 -15,-25 15,-25 30,-15 30,15 15,25 -15,25 -30,15')
          .attr('fill', color)
      } else {
        // 矩形
        node
          .append('rect')
          .attr('x', -50)
          .attr('y', -20)
          .attr('width', 100)
          .attr('height', 40)
          .attr('rx', 5)
          .attr('fill', color)
      }

      // 节点标签
      node
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', d.type === 'condition' ? 5 : 5)
        .attr('fill', 'white')
        .attr('font-size', 12)
        .attr('font-weight', 'bold')
        .text(d.label)
    })

    // 当前执行步骤高亮
    const highlightStep = (step: number) => {
      nodeGroups.selectAll('rect, polygon').attr('opacity', (d: any) => {
        const nodeIndex = mockFlowData.nodes.findIndex((n) => n.id === d.id)
        return nodeIndex <= step ? 1 : 0.3
      })
    }

    // 自动播放
    if (isPlaying) {
      const interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= mockFlowData.nodes.length - 1) {
            setIsPlaying(false)
            clearInterval(interval)
            return prev
          }
          highlightStep(prev + 1)
          return prev + 1
        })
      }, 1000 / speed)

      return () => clearInterval(interval)
    }
  }, [isPlaying, speed, mockFlowData, onNodeClick])

  return (
    <div>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space>
          <Button
            icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? '暂停' : '播放'}
          </Button>
          <Select
            value={speed}
            onChange={setSpeed}
            style={{ width: 100 }}
            options={[
              { value: 0.5, label: '0.5x' },
              { value: 1, label: '1x' },
              { value: 2, label: '2x' },
            ]}
          />
          <span>
            步骤: {currentStep + 1} / {mockFlowData.nodes.length}
          </span>
        </Space>
      </Card>

      <svg
        ref={svgRef}
        style={{ width: '100%', height: 'calc(100vh - 300px)', background: '#fafafa' }}
      />
    </div>
  )
}
