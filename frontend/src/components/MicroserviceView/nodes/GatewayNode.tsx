import { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { Card, Tag } from 'antd'

interface GatewayNodeData {
  label: string
  routeCount?: number
}

function GatewayNode({ data, selected }: NodeProps<GatewayNodeData>) {
  return (
    <>
      <Handle type="target" position={Position.Top} />
      <Card
        size="small"
        style={{
          minWidth: 100,
          backgroundColor: selected ? '#fff7e6' : '#fffbf0',
          borderColor: selected ? '#fa8c16' : '#ffe7ba',
          border: '2px solid #fa8c16',
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 4, textAlign: 'center' }}>
          {data.label || 'API Gateway'}
        </div>
        <div style={{ fontSize: 11, textAlign: 'center', color: '#666' }}>
          <Tag color="orange">{data.routeCount || 0} 条路由</Tag>
        </div>
      </Card>
      <Handle type="source" position={Position.Bottom} />
    </>
  )
}

export default memo(GatewayNode)
