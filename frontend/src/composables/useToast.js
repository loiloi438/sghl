/** Toast global utilisable hors composants (ex. garde de route). */

const listeners = new Set()

export function registerToastHandler(handler) {
  listeners.add(handler)
  return () => listeners.delete(handler)
}

export function showToast(message, type = 'info', duration = 4000) {
  listeners.forEach((handler) => handler(message, type, duration))
}

export function showAccessDenied(message = 'Accès refusé. Vous n\'avez pas les droits pour accéder à cette page.') {
  showToast(message, 'error', 5000)
}
