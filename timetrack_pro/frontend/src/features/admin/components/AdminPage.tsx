import { Link } from 'react-router-dom'
import { Users, DollarSign, FileText, ChevronRight } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

const adminSections = [
  {
    title: 'User Management',
    description: 'Manage users, roles, and deactivation',
    icon: Users,
    href: '/admin/users',
  },
  {
    title: 'Rate Management',
    description: 'Configure billing rates for employees and projects',
    icon: DollarSign,
    href: '/admin/rates',
  },
  {
    title: 'Audit Log',
    description: 'View admin actions and overrides',
    icon: FileText,
    href: '/admin/audit',
  },
]

export function AdminPage() {
  return (
    <div>
      <PageHeader
        title="Admin"
        description="System administration and configuration"
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {adminSections.map((section) => (
          <Link key={section.href} to={section.href}>
            <Card className="h-full transition-colors hover:bg-accent">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <section.icon className="h-5 w-5 text-primary" />
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                </div>
                <CardTitle className="text-lg mt-4">{section.title}</CardTitle>
                <CardDescription>{section.description}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
