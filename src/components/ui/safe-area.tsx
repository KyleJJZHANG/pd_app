import { ReactNode } from 'react';

interface SafeAreaProps {
  children: ReactNode;
  className?: string;
}

export default function SafeArea({ children, className = '' }: SafeAreaProps) {
  return (
    <div className={`pb-safe ${className}`}>
      {children}
    </div>
  );
}