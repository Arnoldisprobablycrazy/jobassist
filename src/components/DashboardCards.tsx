import { LetterText, LucideProps, MessageCircle, Target } from "lucide-react";
import { Card, CardContent, CardDescription, CardTitle } from "./ui/card";

// Renamed interface to avoid conflict with Card component
interface DashboardCard {
    value: number;
    description: string;
    icon: React.ComponentType<LucideProps>;
}

interface CardProps {
    card: DashboardCard;
}

// Individual card component (optional - for better organization)
function DashboardCardItem({ card }: CardProps) {
    const IconComponent = card.icon;
    
    return (
        <Card>
            <CardContent className="p-3">
                <div className="flex flex-col items-center justify-between">

                    <div className="p-3 bg-blue-100 rounded-full">
                        <IconComponent className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="p-3">
                        <CardTitle className="flex justify-center text-2xl font-bold text-texts-cards">{card.value}</CardTitle>
                        <CardDescription className="p-3 text-sm mt-1">{card.description}</CardDescription>
                    </div>
                    
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {cards.map((item) => (
                <DashboardCardItem 
                    key={item.id} 
                    card={item} 
                />
            ))}
        </div>
    );
}