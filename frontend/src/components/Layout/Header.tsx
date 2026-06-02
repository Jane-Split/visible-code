import { Layout, Typography } from 'antd'
import { Link } from 'react-router-dom'

const { Header } = Layout
const { Title } = Typography

export default function AppHeader() {
  return (
    <Header style={{ display: 'flex', alignItems: 'center', background: '#001529', padding: '0 24px' }}>
      <Link to="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
        <Title level={4} style={{ color: 'white', margin: 0 }}>
          CodeViz - 代码可视化分析平台
        </Title>
      </Link>
    </Header>
  )
}
