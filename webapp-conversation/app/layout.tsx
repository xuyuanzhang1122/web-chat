import { getLocaleOnServer } from '@/i18n/server'
import { Providers } from './providers'

import './styles/globals.css'
import './styles/markdown.scss'

const LocaleLayout = async ({
  children,
}: {
  children: React.ReactNode
}) => {
  const locale = await getLocaleOnServer()
  return (
    <html lang={locale ?? 'en'} className="h-full">
      <body className="h-full overflow-hidden">
        <Providers>
          <div className="fixed inset-0 min-w-[300px]">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  )
}

export default LocaleLayout
