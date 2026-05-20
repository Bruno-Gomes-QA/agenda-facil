import { format, formatDistanceToNow, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'

/**
 * Formata uma data ISO para exibição: "19 de maio de 2026"
 */
export function formatDate(iso: string): string {
  return format(parseISO(iso), "d 'de' MMMM 'de' yyyy", { locale: ptBR })
}

/**
 * Formata data + hora: "19 de maio às 14:30"
 */
export function formatDateTime(iso: string): string {
  return format(parseISO(iso), "d 'de' MMMM 'às' HH:mm", { locale: ptBR })
}

/**
 * Apenas hora: "14:30"
 */
export function formatTime(iso: string): string {
  return format(parseISO(iso), 'HH:mm', { locale: ptBR })
}

/**
 * Distância relativa: "há 2 horas", "em 3 dias"
 */
export function fromNow(iso: string): string {
  return formatDistanceToNow(parseISO(iso), { locale: ptBR, addSuffix: true })
}

/**
 * Iniciais do nome para avatar
 */
export function initials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0].toUpperCase())
    .join('')
}
