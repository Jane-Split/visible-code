/**
 * 图数据处理工具 - 大图分块加载与虚拟化
 */

// 节点分块策略
export function chunkNodes(nodes: any[], chunkSize: number = 100) {
  const chunks: any[][] = []
  for (let i = 0; i < nodes.length; i += chunkSize) {
    chunks.push(nodes.slice(i, i + chunkSize))
  }
  return chunks
}

// 可见区域内的节点
export function getVisibleNodes(
  nodes: any[],
  viewport: { x: number; y: number; zoom: number; width: number; height: number }
): any[] {
  const padding = 100 / viewport.zoom
  return nodes.filter((node) => {
    if (!node.position) return true  // 无位置的节点始终显示
    const x = node.position.x
    const y = node.position.y
    return (
      x >= viewport.x - padding &&
      x <= viewport.x + viewport.width / viewport.zoom + padding &&
      y >= viewport.y - padding &&
      y <= viewport.y + viewport.height / viewport.zoom + padding
    )
  })
}

// 搜索节点
export function searchNodes(nodes: any[], query: string): any[] {
  if (!query) return nodes
  const lower = query.toLowerCase()
  return nodes.filter(
    (node) =>
      node.data?.label?.toLowerCase().includes(lower) ||
      node.data?.qualifiedName?.toLowerCase().includes(lower) ||
      node.data?.type?.toLowerCase().includes(lower)
  )
}

// 计算节点布局（简单的力导向布局）
export function calculateLayout(nodes: any[], edges: any[], width: number, height: number) {
  // 简单的网格布局
  const cols = Math.ceil(Math.sqrt(nodes.length))
  const cellWidth = width / (cols + 1)
  const cellHeight = height / (Math.ceil(nodes.length / cols) + 1)

  return nodes.map((node, i) => ({
    ...node,
    position: {
      x: cellWidth * ((i % cols) + 1),
      y: cellHeight * (Math.floor(i / cols) + 1),
    },
  }))
}

// 节点度数统计
export function getNodeDegrees(nodes: any[], edges: any[]): Map<string, number> {
  const degrees = new Map<string, number>()
  nodes.forEach((n) => degrees.set(n.id, 0))
  edges.forEach((e) => {
    degrees.set(e.source, (degrees.get(e.source) || 0) + 1)
    degrees.set(e.target, (degrees.get(e.target) || 0) + 1)
  })
  return degrees
}
