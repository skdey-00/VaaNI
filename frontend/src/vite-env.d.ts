/// <reference types="vite/client" />

declare module 'lucide-react' {
  import { FC, SVGProps } from 'react';
  interface IconProps extends SVGProps<SVGSVGElement> {
    size?: string | number;
  }
  type Icon = FC<IconProps>;
  export const Activity: Icon;
  export const AlertCircle: Icon;
  export const AlertTriangle: Icon;
  export const ArrowLeft: Icon;
  export const ArrowRight: Icon;
  export const BarChart3: Icon;
  export const Calendar: Icon;
  export const Check: Icon;
  export const CheckCircle: Icon;
  export const Circle: Icon;
  export const Clock: Icon;
  export const Cpu: Icon;
  export const Download: Icon;
  export const FileDown: Icon;
  export const FileText: Icon;
  export const Globe: Icon;
  export const Home: Icon;
  export const Languages: Icon;
  export const Lightbulb: Icon;
  export const ListChecks: Icon;
  export const Loader2: Icon;
  export const MessageSquare: Icon;
  export const Mic: Icon;
  export const MicOff: Icon;
  export const Paperclip: Icon;
  export const Printer: Icon;
  export const RotateCcw: Icon;
  export const Scroll: Icon;
  export const Send: Icon;
  export const Sparkles: Icon;
  export const Square: Icon;
  export const Tag: Icon;
  export const Target: Icon;
  export const TrendingUp: Icon;
  export const Wifi: Icon;
  export const WifiOff: Icon;
  export const X: Icon;
  export const XCircle: Icon;
  export const Zap: Icon;
}
