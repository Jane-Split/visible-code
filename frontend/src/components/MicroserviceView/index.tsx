import { useState, useEffect, useCallback } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Card, Tabs, Spin, message } from 'antd'
import { useParams } from 'react-router-dom'
import api from '../../services/api'
import ServiceNode from './nodes/ServiceNode'
import GatewayNode from './nodes/GatewayNode'

const nodeTypes = {
  service: ServiceNode,
  gateway: GatewayNode,
}

interface TopologyData {
  nodes: any[]
  edges: any[]
}

export default function MicroserviceView() {
  const { projectId } = useParams()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('topology')

  const fetchTopology = useCallback(async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const res = await api.get(`/api/projects/${projectId}/microservices/topology`)
      const data = res.data as TopologyData
      
      // 转换为 React Flow 格式
      const flowNodes: Node[] = data.nodes.map((node: any, index: number) => ({
        id: node.id,
        type: node.type || 'service',
        position: {
          x: 250 + (index % 3) * 300,
          y: 100 + Math.floor(index / 3) * 200,
        },
        data: {
          label: node.name,
          status: node.status,
          endpointCount: node.endpoint_count || 0,
        },
      }))
      
      const flowEdges: Edge[] = data.edges.map((edge: any, index: number) => ({
        id: `e${index}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: edge.type === 'sync',
        style: { strokeWidth: 2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#1890ff',
        },
        label: edge.type === 'async' ? '异步' : '',
      }))
      
      setNodes(flowNodes)
      setEdges(flowEdges)
    } catch (error) {
      message.error('获取服务拓扑失败')
    } finally {
      setLoading(false)
    }
  }, [projectId, setNodes, setEdges])

  useEffect(() => {
    if (activeTab === 'topology') {
      fetchTopology()
    }
  }, [activeTab, fetchTopology])

  return (
    <div>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            { key: 'topology', label: '服务拓扑图' },
            { key: 'routes', label: '网关路由' },
            { key: 'calls', label: '调用链路' },
          ]}
        />
      </Card>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
          <Spin size="large" tip="加载中..." />
        </div>
      ) : activeTab === 'topology' ? (
        <div style={{ height: 'calc(100vh - 300px)' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
            <Background color="#aaa" gap={16} />
          </ReactFlow>
        </div>
      ) : (
        <div style={{ padding: 20 }}>
          <p>更多视图功能开发中...</p>
        </div>
      )}
    </div>
  )
}
