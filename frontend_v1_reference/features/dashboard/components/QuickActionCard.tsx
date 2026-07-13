import {

Card,

CardContent,

CardHeader,

CardTitle,

} from "@/components/ui/Card";

import { Button } from "@/components/ui/Button";

type Action={

title:string;

onClick:()=>void;

};

type Props={

actions:Action[];

};

export function QuickActionCard({

actions,

}:Props){

return(

<Card variant="elevated">

<CardHeader>

<CardTitle>

Quick Actions

</CardTitle>

</CardHeader>

<CardContent className="grid gap-3">

{

actions.map((action)=>(

<Button

key={action.title}

variant="secondary"

fullWidth

onClick={action.onClick}

>

{action.title}

</Button>

))

}

</CardContent>

</Card>

);

}