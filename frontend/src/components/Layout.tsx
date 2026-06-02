import { Outlet } from 'react-router-dom'
import { Layout as AntLayout, Menu, Typography } from 'antd'
import { HomeOutlined, ProjectOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Header, Sider, Content } = AntLayout
const { Title } = Typography

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()

  const selectedKey = location.pathname.split('/')[1] || 'projects'

  const menuItems = [
    { key: 'projects', icon: <ProjectOutlined />, label: '项目列表' },
    { key: 'about', icon: <HomeOutlined />, label: '关于' },
  ]

  return (
    <AntLayout style={{ height: '100vh' }}>
      <Header style={{
        background: '#001529',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center'
      }}>
        <Title level={4} style={{ color: 'white', margin: 0 }}>
          CodeViz - 代码可视化平台
        </Title>
      </Header>
      <AntLayout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={({ key }) => navigate(`/${key}`)}
          />
        </Sider>
        <Content style={{ padding: '16px', overflow: 'auto' }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  )
}
