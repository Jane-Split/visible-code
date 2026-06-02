import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Card, Select, Space, Table, Tag, Empty } from 'antd'
import { useParams } from 'react-router-dom'
import api from '../../services/api'

interface DataFlowNode {
  id: string
  name: string
  type: 'input' | 'process' | 'storage' | 'output'
  service?: string
}

interface DataFlowEdge {
  source: string
  target: string
  dataField?: string
}

export default function DataFlowView() {
  const { projectId } = useParams()
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedEntity, setSelectedEntity] = useState<string>()
  const [dataFlow, setDataFlow] = useState<{ nodes: DataFlowNode[]; edges: DataFlowEdge[] }>({
    nodes: [],
    edges: [],
  })

  // 模拟数据流数据
  const mockDataFlow: { nodes: DataFlowNode[]; edges: DataFlowEdge[] } = {
    nodes: [
      { id: 'request', name: 'HTTP Request', type: 'input', service: 'Gateway' },
      { id: 'validate', name: '参数校验', type: 'process', service: 'user-service' },
      { id: 'transform', name: '数据转换', type: 'process', service: 'user-service' },
      { id: 'db', name: 'User Database', type: 'storage' },
      { id: 'cache', name: 'Redis Cache', type: 'storage' },
      { id: 'response', name: 'HTTP Response', type: 'output' },
    ],
    edges: [
      { source: 'request', target: 'validate', dataField: 'userId' },
      { source: 'validate', target: 'transform', dataField: 'userData' },
      { source: 'transform', target: 'cache', dataField: 'cachedUser' },
      { source: 'transform', target: 'db', dataField: 'userRecord' },
      { source: 'cache', target: 'response', dataField: 'cachedUser' },
      { source: 'db', target: 'response', dataField: 'userRecord' },
    ],
  }

  useEffect(() => {
    setDataFlow(mockDataFlow)
  }, [])

  useEffect(() => {
    if (!svgRef.current || dataFlow.nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    svg.selectAll('*').remove()

    // 箭头标记
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'data-arrow')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .append('path')
      .attr('d', 'M 0,-5 L 10,0 L 0,5')
      .attr('fill', '#52c41a')

    const g = svg.append('g')

    // 节点颜色
    const nodeColors = {
      input: '#1890ff',
      process: '#722ed1',
      storage: '#fa8c16',
      output: '#52c41a',
    }

    // 节点图标
    const nodeIcons = {
      input: '→',
      process: '◉',
      storage: '⬢',
      output: '←',
    }

    // 布局
    const nodeCount = dataFlow.nodes.length
    const spacing = width / (nodeCount + 1)

    const nodePositions: Record<string, { x: number; y: number }> = {}
    dataFlow.nodes.forEach((node, i) => {
      nodePositions[node.id] = { x: spacing * (i + 1), y: height / 2 }
    })

    // 绘制边
    g.append('g')
      .attr('class', 'edges')
      .selectAll('path')
      .data(dataFlow.edges)
      .enter()
      .append('path')
      .attr('d', (d) => {
        const source = nodePositions[d.source]
        const target = nodePositions[d.target]
        const midX = (source.x + target.x) / 2
        return `M ${source.x} ${source.y} C ${midX} ${source.y} ${midX} ${target.y} ${target.x} ${target.y}`
      })
      .attr('fill', 'none')
      .attr('stroke', '#52c41a')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .attr('marker-end', 'url(#data-arrow)')

    // 边标签
    g.append('g')
      .attr('class', 'edge-labels')
      .selectAll('text')
      .data(dataFlow.edges)
      .enter()
      .append('text')
      .text((d) => d.dataField || '')
      .attr('x', (d) => (nodePositions[d.source].x + nodePositions[d.target].x) / 2)
      .attr('y', (d) => (nodePositions[d.source].y + nodePositions[d.target].y) / 2 - 10)
      .attr('text-anchor', 'middle')
      .attr('font-size', 11)
      .attr('fill', '#52c41a')

    // 绘制节点
    const nodes = g
      .append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(dataFlow.nodes)
      .enter()
      .append('g')
      .attr('transform', (d) => `translate(${nodePositions[d.id].x}, ${nodePositions[d.id].y})`)

    // 节点圆形背景
    nodes
      .append('circle')
      .attr('r', 30)
      .attr('fill', (d) => nodeColors[d.type])
      .attr('opacity', 0.2)

    // 节点图标
    nodes
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 5)
      .attr('font-size', 20)
      .attr('fill', (d) => nodeColors[d.type])
      .text((d) => nodeIcons[d.type])

    // 节点标签
    nodes
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('y', 50)
      .attr('font-size', 12)
      .attr('font-weight', 'bold')
      .text((d) => d.name)

    // 节点服务标签
    nodes
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('y', 65)
      .attr('font-size', 10)
      .attr('fill', '#999')
      .text((d) => d.service || '')
  }, [dataFlow])

  const columns = [
    {
      title: '数据字段',
      dataIndex: 'dataField',
      key: 'dataField',
    },
    {
      title: '源节点',
      dataIndex: 'source',
      key: 'source',
    },
    {
      title: '目标节点',
      dataIndex: 'target',
      key: 'target',
    },
    {
      title: '类型',
      key: 'type',
      render: (_: any, record: DataFlowEdge) => (
        <Tag color="green">{record.dataField ? '数据传递' : '控制流'}</Tag>
      ),
    },
  ]

  return (
    <div>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="选择实体查看数据流"
            style={{ width: 200 }}
            value={selectedEntity}
            onChange={setSelectedEntity}
            allowClear
            options={[
              { value: 'user', label: 'UserService' },
              { value: 'order', label: 'OrderService' },
              { value: 'payment', label: 'PaymentService' },
            ]}
          />
        </Space>
      </Card>

      <div style={{ display: 'flex', gap: 16 }}>
        <Card title="数据流向图" style={{ flex: 1 }}>
          {dataFlow.nodes.length > 0 ? (
            <svg
              ref={svgRef}
              style={{ width: '100%', height: 300, background: '#fafafa' }}
            />
          ) : (
            <Empty description="请选择一个实体查看数据流" />
          )}
        </Card>

        <Card title="数据血缘表" style={{ width: 400 }}>
          <Table
            size="small"
            dataSource={dataFlow.edges.map((e, i) => ({ key: i, ...e }))}
            columns={columns}
            pagination={false}
          />
        </Card>
      </div>
    </div>
  )
}
