import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import { PipelineMetrics } from "@/types/recruiting";

export function PipelineMetricsCard({ metrics }: { metrics: PipelineMetrics }) {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <Card className="border-green-500/20 bg-card/90 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                SOURCED
              </p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                {metrics.sourced}
              </p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card className="border-red-500/20 bg-card/90 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                ADVANCED
              </p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                {metrics.advanced}
              </p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
              <TrendingDown className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

