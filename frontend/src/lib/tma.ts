export function getTmaInitData(): string {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return encodeURIComponent(window.Telegram.WebApp.initData);
  }
  return '';
}
