/**
 * 图表导出工具
 */

// 导出为 PNG
export async function exportToPNG(elementId: string, filename: string = 'graph.png'): Promise<void> {
  const element = document.getElementById(elementId)
  if (!element) {
    throw new Error(`Element ${elementId} not found`)
  }

  // 使用 html2canvas
  const html2canvas = (await import('html2canvas')).default
  const canvas = await html2canvas(element, {
    backgroundColor: '#ffffff',
    scale: 2,
  })

  // 下载
  const link = document.createElement('a')
  link.download = filename
  link.href = canvas.toDataURL('image/png')
  link.click()
}

// 导出为 SVG
export function exportToSVG(elementId: string, filename: string = 'graph.svg'): void {
  const element = document.getElementById(elementId)
  if (!element) {
    throw new Error(`Element ${elementId} not found`)
  }

  const svgElement = element.querySelector('svg')
  if (!svgElement) {
    throw new Error('No SVG element found')
  }

  const svgData = new XMLSerializer().serializeToString(svgElement)
  const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.download = filename
  link.href = url
  link.click()
  URL.revokeObjectURL(url)
}

// 导出为 JSON
export function exportToJSON(data: any, filename: string = 'graph.json'): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.download = filename
  link.href = url
  link.click()
  URL.revokeObjectURL(url)
}

// 导出为 PDF（简化版 - 使用打印）
export function exportToPDF(elementId: string, filename: string = 'graph.pdf'): void {
  const element = document.getElementById(elementId)
  if (!element) {
    throw new Error(`Element ${elementId} not found`)
  }

  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>${filename}</title>
          <style>
            body { margin: 0; padding: 20px; }
            .graph-container { width: 100%; }
            svg { width: 100%; height: auto; }
          </style>
        </head>
        <body>
          <div class="graph-container">
            ${element.innerHTML}
          </div>
          <script>
            window.onload = function() {
              window.print();
              window.close();
            }
          </script>
        </body>
      </html>
    `)
    printWindow.document.close()
  }
}
