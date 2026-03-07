'use client'

import { useState } from 'react'
import { Menu } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Sidebar } from '@/components/layout/Sidebar'

export function MobileNav() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={() => setOpen(true)}
        aria-label="Open navigation"
      >
        <Menu className="h-6 w-6" />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="p-0 w-64 h-full max-h-screen top-0 left-0 translate-x-0 translate-y-0 rounded-none data-[state=open]:slide-in-from-left">
          <Sidebar onClose={() => setOpen(false)} />
        </DialogContent>
      </Dialog>
    </>
  )
}
