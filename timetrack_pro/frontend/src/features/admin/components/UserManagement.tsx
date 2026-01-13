import { Users } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { EmptyState } from '@/components/common/EmptyState'

export function UserManagement() {
  return (
    <div>
      <PageHeader
        title="User Management"
        description="View and manage system users"
      />

      <Card>
        <CardContent className="p-0">
          <EmptyState
            icon={Users}
            title="User management"
            description="User listing and management will be implemented here"
          />
        </CardContent>
      </Card>
    </div>
  )
}
