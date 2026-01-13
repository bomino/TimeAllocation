import { DollarSign } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { EmptyState } from '@/components/common/EmptyState'

export function RateManagement() {
  return (
    <div>
      <PageHeader
        title="Rate Management"
        description="Configure billing rates"
      />

      <Card>
        <CardContent className="p-0">
          <EmptyState
            icon={DollarSign}
            title="Rate management"
            description="Rate configuration will be implemented here"
          />
        </CardContent>
      </Card>
    </div>
  )
}
