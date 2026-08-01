import React from 'react';
import { FaExclamationTriangle, FaHardHat, FaVest, FaExclamationCircle } from 'react-icons/fa';

const StatsCards = ({ alerts }) => {
  // Calculate statistics from alerts
  const stats = {
    total: alerts.length,
    noHelmet: alerts.filter(alert => alert.violation === 'No Helmet').length,
    noVest: alerts.filter(alert => alert.violation === 'No Vest').length,
    both: alerts.filter(alert => 
      alert.violation === 'No Helmet, No Vest' || 
      alert.violation === 'No Helmet + No Vest'
    ).length,
  };

  const cards = [
    {
      title: 'Total Alerts',
      value: stats.total,
      icon: FaExclamationTriangle,
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'No Helmet',
      value: stats.noHelmet,
      icon: FaHardHat,
      color: 'bg-orange-500',
      textColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: 'No Vest',
      value: stats.noVest,
      icon: FaVest,
      color: 'bg-yellow-500',
      textColor: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'No Helmet + No Vest',
      value: stats.both,
      icon: FaExclamationCircle,
      color: 'bg-red-500',
      textColor: 'text-red-600',
      bgColor: 'bg-red-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div
            key={index}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium mb-1">{card.title}</p>
                <p className={`text-3xl font-bold ${card.textColor}`}>{card.value}</p>
              </div>
              <div className={`${card.bgColor} p-3 rounded-full`}>
                <Icon className={`text-2xl ${card.textColor}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatsCards;
