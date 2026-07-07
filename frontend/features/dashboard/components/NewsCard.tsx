import {

Card,

CardContent,

CardHeader,

CardTitle,

} from "@/components/ui/Card";

type News = {

title:string;

source:string;

time:string;

};

type Props={

items:News[];

};

export function NewsCard({

items,

}:Props){

return(

<Card variant="elevated">

<CardHeader>

<CardTitle>

Latest News

</CardTitle>

</CardHeader>

<CardContent className="space-y-4">

{

items.map((item,index)=>(

<div

key={index}

className="border-b pb-3 last:border-none"

>

<p className="font-medium">

{item.title}

</p>

<p className="mt-1 text-sm text-[#5B6473]">

{item.source}

•

{item.time}

</p>

</div>

))

}

</CardContent>

</Card>

);

}