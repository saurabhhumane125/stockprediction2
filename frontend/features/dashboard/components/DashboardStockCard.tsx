import { Building2 } from "lucide-react";

import {

Card,

CardHeader,

CardTitle,

CardContent,

} from "@/components/ui/Card";

import type {

StockOverviewViewModel,

} from "../types/dashboard.view.types";

interface Props{

stock:StockOverviewViewModel;

}

export function DashboardStockCard({

stock,

}:Props){

return(

<Card variant="elevated">

<CardHeader>

<CardTitle>

Stock

</CardTitle>

</CardHeader>

<CardContent className="space-y-3">

<div className="flex items-center gap-3">

<Building2 size={22}/>

<div>

<p className="font-semibold">

{stock.symbol}

</p>

<p className="text-sm text-slate-500">

{stock.companyName}

</p>

</div>

</div>

<p className="text-sm">

Sector

</p>

<p className="font-medium">

{stock.sector}

</p>

</CardContent>

</Card>

);

}