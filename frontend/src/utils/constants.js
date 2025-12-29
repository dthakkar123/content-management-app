// Content source types
export const SOURCE_TYPES = {
  TWITTER: 'twitter',
  PDF: 'pdf',
  ARXIV: 'arxiv',
  ACM: 'acm',
  WEB: 'web',
};

// Source type labels for UI
export const SOURCE_TYPE_LABELS = {
  [SOURCE_TYPES.TWITTER]: 'Twitter',
  [SOURCE_TYPES.PDF]: 'PDF',
  [SOURCE_TYPES.ARXIV]: 'arXiv',
  [SOURCE_TYPES.ACM]: 'ACM Digital Library',
  [SOURCE_TYPES.WEB]: 'Web Article',
};

// Source type colors for badges
export const SOURCE_TYPE_COLORS = {
  [SOURCE_TYPES.TWITTER]: 'bg-blue-100 text-blue-800',
  [SOURCE_TYPES.PDF]: 'bg-red-100 text-red-800',
  [SOURCE_TYPES.ARXIV]: 'bg-green-100 text-green-800',
  [SOURCE_TYPES.ACM]: 'bg-purple-100 text-purple-800',
  [SOURCE_TYPES.WEB]: 'bg-gray-100 text-gray-800',
};

// Job statuses
export const JOB_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

// Pagination
export const DEFAULT_PAGE_SIZE = 10;
export const MAX_PAGE_SIZE = 50;

// File upload
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const ALLOWED_FILE_TYPES = ['.pdf'];

// Theme colors
export const THEME_COLORS = [
  '#FF5733', '#33FF57', '#3357FF', '#F333FF', '#FF33F3',
  '#33FFF3', '#F3FF33', '#FF8C33', '#8C33FF', '#33FF8C',
];
