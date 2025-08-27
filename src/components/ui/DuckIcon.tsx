import React from 'react';
import { cn } from '@/lib/utils';

export type DuckIconVariant = 'head' | 'letter';
export type DuckIconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';
export type DuckIconBackground = 'none' | 'soft' | 'warm' | 'transparent';

interface DuckIconProps {
  variant?: DuckIconVariant;
  size?: DuckIconSize;
  className?: string;
  animated?: boolean;
  background?: DuckIconBackground;
  onClick?: () => void;
}

const sizeClasses: Record<DuckIconSize, string> = {
  xs: 'w-3 h-3 sm:w-4 sm:h-4',
  sm: 'w-5 h-5 sm:w-6 sm:h-6', 
  md: 'w-6 h-6 sm:w-8 sm:h-8',
  lg: 'w-10 h-10 sm:w-12 sm:h-12',
  xl: 'w-12 h-12 sm:w-16 sm:h-16',
  '2xl': 'w-16 h-16 sm:w-20 sm:h-20',
  '3xl': 'w-20 h-20 sm:w-24 sm:h-24'
};

const DuckIcon: React.FC<DuckIconProps> = ({ 
  variant = 'head', 
  size = 'md', 
  className = '',
  animated = false,
  background = 'soft',
  onClick
}) => {
  const imageSrc = variant === 'head' ? '/icon/pd.png' : '/icon/image.png';
  const alt = variant === 'head' ? '心理鸭头像' : '心理鸭信使';
  
  const baseClasses = cn(
    'object-contain select-none transition-all duration-300',
    sizeClasses[size],
    onClick && 'cursor-pointer hover:scale-110 active:scale-95 hover:drop-shadow-md touch-manipulation',
    className
  );

  const animationClass = animated ? (
    variant === 'letter' ? 'animate-duck-breathe' : 'animate-duck-float'
  ) : '';

  // 背景处理逻辑
  const getBackgroundClasses = () => {
    if (background === 'none') return '';
    
    const baseBackground = 'rounded-full';
    
    switch (background) {
      case 'soft':
        return `${baseBackground} bg-gradient-to-br from-white/8 to-white/3 backdrop-blur-sm`;
      case 'warm': 
        return `${baseBackground} bg-gradient-to-br from-amber-100/20 to-orange-100/10 backdrop-blur-sm`;
      case 'transparent':
        return `${baseBackground} bg-white/5`;
      default:
        return `${baseBackground} bg-white/8`;
    }
  };

  // 为不同variant添加特殊效果
  const variantClasses = cn(
    'drop-shadow-sm hover:drop-shadow-md transition-all duration-300',
    getBackgroundClasses(),
    variant === 'letter' ? 'p-1' : 'p-0.5'
  );

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={cn(baseClasses, animationClass, variantClasses)}
      onClick={onClick}
      draggable={false}
      loading="lazy"
      style={{ WebkitTapHighlightColor: 'transparent' }}
    />
  );
};

export default DuckIcon;