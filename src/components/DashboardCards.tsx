import { LetterText, LucideProps, MessageCircle, Target } from "lucide-react";
import { Card, CardContent, CardDescription, CardTitle } from "./ui/card";

interface DashboardCard {
    value: number;
    description: string;
    icon: React.ComponentType<LucideProps>;
}
interface CardProps{
    card:DashboardCard;
}

function DashboardCardItem({ card }: CardProps) {
    const IconComponent = card.icon;
    
    return (
        <Card className="hover:shadow-md transition-all duration-200 border">
            <CardContent className="p-4">
                <div className="flex flex-col items-center text-center space-y-3">
                    <div className="p-2 bg-blue-50 rounded-full">
                        <IconComponent className="w-4 h-4 text-blue-600" />
                    </div>
                    <CardTitle className="text-xl font-bold text-texts-cards">
                        {card.value}
                    </CardTitle>
                    <CardDescription className="text-xs text-gray-600 leading-tight">
                        {card.description}
                    </CardDescription>
                </div>
            </CardContent>
        </Card>
    );
}

export default function DashboardCards() {
    const cards = [
        {
            id: 1,
            icon: LetterText,
            value: 12,
            description: 'Total Cover Letters',
        },
        {
            id: 2,
            icon: Target,
            value: 85,
            description: 'Average Match Score',
        },
        {
            id: 3,
            icon: MessageCircle,
            value: 7,
            description: 'Feedback Received',
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {cards.map((item) => (
                <DashboardCardItem 
                    key={item.id} 
                    card={item} 
                />
            ))}
        </div>
    );
}