/**
 * Utility formatters for display.
 */

export function formatDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function formatConfidence(confidence) {
  return `${(confidence * 100).toFixed(1)}%`;
}

export function truncateText(text, maxLength = 80) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function getSeverityColor(severity) {
  const colors = {
    high: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/30' },
    medium: { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/30' },
    low: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30' },
    none: { bg: 'bg-primary-500/20', text: 'text-primary-400', border: 'border-primary-500/30' },
  };
  return colors[severity] || colors.medium;
}

export function getSeverityLabel(severity) {
  const labels = {
    high: 'High Severity',
    medium: 'Medium Severity',
    low: 'Low Severity',
    none: 'Healthy',
  };
  return labels[severity] || severity;
}
