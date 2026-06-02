import { Typography, Card, Space } from 'antd'

const { Title, Text } = Typography

export default function ArchitectureView() {
  return (
    <div style={{ padding: 20 }}>
      <Card>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Title level={4}>架构图</Title>
          <Text type="secondary">
            项目架构可视化将在此区域展示。
          </Text>
          <div style={{
            height: 400,
            border: '1px dashed #d9d9d9',
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#fafafa'
          }}>
            <Text>架构图加载中...</Text>
          </div>
        </Space>
      </Card>
    </div>
  )
}
