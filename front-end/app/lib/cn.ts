import { type ClassValue, clsx } from 'clsx'

// Utilitário para mesclar classes Tailwind condicionalmente
// Uso: cn('base-class', condition && 'conditional-class', { 'another': isTrue })
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs)
}
