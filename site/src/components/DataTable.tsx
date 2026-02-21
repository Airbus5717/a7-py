import type { ReactNode } from 'react'

interface DataTableProps {
  headers: string[]
  rows: ReactNode[][]
  caption?: string
  rowHeaderColumn?: number | null
}

export default function DataTable({ headers, rows, caption, rowHeaderColumn = 0 }: DataTableProps) {
  return (
    <div className="doc-table-wrap">
      <table className="doc-table">
        {caption ? <caption className="doc-table-caption">{caption}</caption> : null}
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header} scope="col">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              {row.map((cell, cellIndex) => (
                cellIndex === rowHeaderColumn ? (
                  <th key={cellIndex} scope="row">
                    {cell}
                  </th>
                ) : (
                  <td key={cellIndex}>{cell}</td>
                )
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
