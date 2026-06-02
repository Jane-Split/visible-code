import { useCallback, useState, useEffect, useMemo } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Card, Input, Space, Spin, message } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import { useParams } from 'react-router-dom'
import api from '../../services/api'
import ModuleNode from './nodes/ModuleNode'
import ClassNode from './nodes/ClassNode'
import MethodNode from './nodes/MethodNode'
import './index.css'

const nodeTypes: NodeTypes = {
  module: ModuleNode,
  class: ClassNode,
  interface: ClassNode,
  function: MethodNode,
  method: MethodNode,
}

interface GraphData {
  nodes: any[]
  edges: any[]
  total_nodes: number
  total_edges: number
}

function ArchitectureViewInner() {
  const { projectId } = useParams()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const { fitView } = useReactFlow()

  useEffect(() => {
    if (projectId) {
      fetchGraph()
    }
  }, [projectId])

  const fetchGraph = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/projects/${projectId}/graphs/dependency`)
      const data = res.data as GraphData
      setGraphData(data)

      // 转换为 React Flow 格式
      const flowNodes: Node[] = data.nodes.map((node: any) => ({
        id: node.id,
        type: node.type || 'class',
        position: { x: 0, y: 0 }, // 后续使用布局算法
        data: {
          label: node.name,
          type: node.type,
          qualifiedName: node.qualified_name,
          filePath: node.file_path,
          modifiers: node.modifiers || [],
          annotations: node.annotations || [],
        },
      }))

      const flowEdges: Edge[] = data.edges.map((edge: any) => ({
        id: `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: edge.type === 'call',
        label: edge.type,
        style: { strokeWidth: 2 },
      }))

      setNodes(flowNodes)
      setEdges(flowEdges)

      // 自动布局
      setTimeout(() => fitView({ padding: 0.2 }), 100)
    } catch (error) {
      message.error('获取依赖图失败')
    } finally {
      setLoading(false)
    }
  }

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  // 搜索过滤
  const filteredNodes = useMemo(() => {
    if (!searchText) return nodes
    return nodes.filter(
      (node) =>
        node.data.label.toLowerCase().includes(searchText.toLowerCase()) ||
        node.data.qualifiedName?.toLowerCase().includes(searchText.toLowerCase())
    )
  }, [nodes, searchText])

  // 高亮搜索结果
  const highlightedNodes = useMemo(() => {
    return filteredNodes.map((node) => ({
      ...node,
      style: searchText
        ? {
            backgroundColor: node.data.label.toLowerCase().includes(searchText.toLowerCase())
              ? '#fffbe6'
              : '#f5f5f5',
          }
        : {},
    }))
  }, [filteredNodes, searchText])

  return (
    <div style={{ height: 'calc(100vh - 200px)' }}>
      <Card
        size="small"
        style={{ marginBottom: 16, position: 'sticky', top: 0, zIndex: 10 }}
      >
        <Space>
          <Input
            placeholder="搜索类/方法..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 200 }}
          />
          <span>
            显示 {highlightedNodes.length} / {nodes.length} 个节点
          </span>
          <span>
            {edges.length} 条边
          </span>
        </Space>
      </Card>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
          <Spin size="large" tip="加载中..." />
        </div>
      ) : (
        <ReactFlow
          nodes={highlightedNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls />
          <Background color="#aaa" gap={16} />
        </ReactFlow>
      )}
    </div>
  )
}

export default function ArchitectureView() {
  return (
    <ReactFlowProvider>
      <ArchitectureViewInner />
    </ReactFlowProvider>
  )
}
