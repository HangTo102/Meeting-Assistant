export function sanitizeHtml(content) {
  if (!content) return ''
  return String(content)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
    .replace(/&lt;br\s*\/?&gt;/gi, '<br>')
}
