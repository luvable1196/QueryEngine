// Animation utility functions and configurations

// Easing functions
export const easingFunctions = {
  linear: (t) => t,
  easeInQuad: (t) => t * t,
  easeOutQuad: (t) => t * (2 - t),
  easeInOutQuad: (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  easeInCubic: (t) => t * t * t,
  easeOutCubic: (t) => (--t) * t * t + 1,
  easeInOutCubic: (t) => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
  easeInQuart: (t) => t * t * t * t,
  easeOutQuart: (t) => 1 - (--t) * t * t * t,
  easeInOutQuart: (t) => t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t,
  easeInQuint: (t) => t * t * t * t * t,
  easeOutQuint: (t) => 1 + (--t) * t * t * t * t,
  easeInOutQuint: (t) => t < 0.5 ? 16 * t * t * t * t * t : 1 + 16 * (--t) * t * t * t * t,
  easeInSine: (t) => 1 - Math.cos((t * Math.PI) / 2),
  easeOutSine: (t) => Math.sin((t * Math.PI) / 2),
  easeInOutSine: (t) => -(Math.cos(Math.PI * t) - 1) / 2,
  easeInExpo: (t) => t === 0 ? 0 : Math.pow(2, 10 * (t - 1)),
  easeOutExpo: (t) => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
  easeInOutExpo: (t) => {
    if (t === 0) return 0;
    if (t === 1) return 1;
    if (t < 0.5) return Math.pow(2, 20 * t - 10) / 2;
    return (2 - Math.pow(2, -20 * t + 10)) / 2;
  },
  easeInCirc: (t) => 1 - Math.sqrt(1 - t * t),
  easeOutCirc: (t) => Math.sqrt(1 - (t - 1) * (t - 1)),
  easeInOutCirc: (t) => t < 0.5 ? (1 - Math.sqrt(1 - 4 * t * t)) / 2 : (Math.sqrt(1 - (-2 * t + 2) * (-2 * t + 2)) + 1) / 2,
  easeInBack: (t) => {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return c3 * t * t * t - c1 * t * t;
  },
  easeOutBack: (t) => {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  },
  easeInOutBack: (t) => {
    const c1 = 1.70158;
    const c2 = c1 * 1.525;
    return t < 0.5
      ? (Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
      : (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2;
  },
  easeInElastic: (t) => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0
      ? 0
      : t === 1
      ? 1
      : -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * c4);
  },
  easeOutElastic: (t) => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0
      ? 0
      : t === 1
      ? 1
      : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  },
  easeInOutElastic: (t) => {
    const c5 = (2 * Math.PI) / 4.5;
    return t === 0
      ? 0
      : t === 1
      ? 1
      : t < 0.5
      ? -(Math.pow(2, 20 * t - 10) * Math.sin((20 * t - 11.125) * c5)) / 2
      : (Math.pow(2, -20 * t + 10) * Math.sin((20 * t - 11.125) * c5)) / 2 + 1;
  },
  easeInBounce: (t) => 1 - easingFunctions.easeOutBounce(1 - t),
  easeOutBounce: (t) => {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) {
      return n1 * t * t;
    } else if (t < 2 / d1) {
      return n1 * (t -= 1.5 / d1) * t + 0.75;
    } else if (t < 2.5 / d1) {
      return n1 * (t -= 2.25 / d1) * t + 0.9375;
    } else {
      return n1 * (t -= 2.625 / d1) * t + 0.984375;
    }
  },
  easeInOutBounce: (t) => {
    return t < 0.5
      ? (1 - easingFunctions.easeOutBounce(1 - 2 * t)) / 2
      : (1 + easingFunctions.easeOutBounce(2 * t - 1)) / 2;
  }
};



// Animation configurations
export const animationConfigs = {
  fast: { duration: 200, easing: easingFunctions.easeOutQuad },
  normal: { duration: 300, easing: easingFunctions.easeOutCubic },
  slow: { duration: 500, easing: easingFunctions.easeOutQuart },
  smooth: { duration: 400, easing: easingFunctions.easeInOutQuad },
  bounce: { duration: 600, easing: easingFunctions.easeOutBounce },
  elastic: { duration: 800, easing: easingFunctions.easeOutElastic },
  spring: { duration: 400, easing: easingFunctions.easeOutBack }
};

// Animation presets
export const animationPresets = {
  slideIn: {
    from: { transform: 'translateX(-100%)', opacity: 0 },
    to: { transform: 'translateX(0)', opacity: 1 },
    ...animationConfigs.smooth
  },
  slideOut: {
    from: { transform: 'translateX(0)', opacity: 1 },
    to: { transform: 'translateX(100%)', opacity: 0 },
    ...animationConfigs.smooth
  },
  fadeIn: {
    from: { opacity: 0 },
    to: { opacity: 1 },
    ...animationConfigs.normal
  },
  fadeOut: {
    from: { opacity: 1 },
    to: { opacity: 0 },
    ...animationConfigs.normal
  },
  scaleIn: {
    from: { transform: 'scale(0)', opacity: 0 },
    to: { transform: 'scale(1)', opacity: 1 },
    ...animationConfigs.bounce
  },
  scaleOut: {
    from: { transform: 'scale(1)', opacity: 1 },
    to: { transform: 'scale(0)', opacity: 0 },
    ...animationConfigs.normal
  },
  slideUp: {
    from: { transform: 'translateY(100%)', opacity: 0 },
    to: { transform: 'translateY(0)', opacity: 1 },
    ...animationConfigs.smooth
  },
  slideDown: {
    from: { transform: 'translateY(-100%)', opacity: 0 },
    to: { transform: 'translateY(0)', opacity: 1 },
    ...animationConfigs.smooth
  },
  rotateIn: {
    from: { transform: 'rotate(-180deg)', opacity: 0 },
    to: { transform: 'rotate(0deg)', opacity: 1 },
    ...animationConfigs.elastic
  },
  flip: {
    from: { transform: 'rotateY(0deg)' },
    to: { transform: 'rotateY(180deg)' },
    ...animationConfigs.smooth
  },
  bounce: {
    from: { transform: 'translateY(0px)' },
    to: { transform: 'translateY(-10px)' },
    ...animationConfigs.bounce
  },
  pulse: {
    from: { transform: 'scale(1)' },
    to: { transform: 'scale(1.05)' },
    ...animationConfigs.normal
  },
  wiggle: {
    keyframes: [
      { transform: 'rotate(0deg)' },
      { transform: 'rotate(3deg)' },
      { transform: 'rotate(-3deg)' },
      { transform: 'rotate(0deg)' }
    ],
    duration: 500,
    easing: easingFunctions.easeInOutSine
  },
  shake: {
    keyframes: [
      { transform: 'translateX(0)' },
      { transform: 'translateX(-2px)' },
      { transform: 'translateX(2px)' },
      { transform: 'translateX(-2px)' },
      { transform: 'translateX(2px)' },
      { transform: 'translateX(0)' }
    ],
    duration: 400,
    easing: easingFunctions.easeInOutSine
  },
  rubber: {
    keyframes: [
      { transform: 'scale(1)' },
      { transform: 'scale(1.25, 0.75)' },
      { transform: 'scale(0.75, 1.25)' },
      { transform: 'scale(1.15, 0.85)' },
      { transform: 'scale(0.95, 1.05)' },
      { transform: 'scale(1)' }
    ],
    duration: 1000,
    easing: easingFunctions.easeInOutSine
  }
};

// Animation utilities
export const animateElement = (element, preset, options = {}) => {
  if (!element || !preset) return Promise.resolve();

  const config = { ...preset, ...options };
  const { from, to, keyframes, duration, easing } = config;

  return new Promise((resolve) => {
    if (keyframes) {
      element.animate(keyframes, {
        duration,
        easing: easing.name || 'ease-out',
        fill: 'forwards'
      }).addEventListener('finish', resolve);
    } else {
      element.animate([from, to], {
        duration,
        easing: easing.name || 'ease-out',
        fill: 'forwards'
      }).addEventListener('finish', resolve);
    }
  });
};

// Stagger animation utility
export const staggerAnimation = (elements, preset, staggerDelay = 100) => {
  const promises = elements.map((element, index) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        animateElement(element, preset).then(resolve);
      }, index * staggerDelay);
    });
  });

  return Promise.all(promises);
};

// Chain multiple animations
export const chainAnimations = async (element, animations) => {
  for (const animation of animations) {
    await animateElement(element, animation);
  }
};

// Parallel animations
export const parallelAnimations = (elements, preset) => {
  const promises = elements.map(element => animateElement(element, preset));
  return Promise.all(promises);
};

// Generate random animation delay
export const randomDelay = (min = 0, max = 1000) => {
  return Math.random() * (max - min) + min;
};

// Generate random animation duration
export const randomDuration = (min = 300, max = 1000) => {
  return Math.random() * (max - min) + min;
};

// Get animation class names for Tailwind
export const getAnimationClasses = (type, options = {}) => {
  const baseClasses = {
    fadeIn: 'animate-fade-in',
    slideUp: 'animate-slide-up',
    slideDown: 'animate-slide-down',
    slideLeft: 'animate-slide-left',
    slideRight: 'animate-slide-right',
    bounceIn: 'animate-bounce-in',
    scaleIn: 'animate-scale-in',
    rotateIn: 'animate-rotate-in',
    float: 'animate-float',
    pulse: 'animate-pulse',
    bounce: 'animate-bounce',
    spin: 'animate-spin',
    ping: 'animate-ping',
    wiggle: 'animate-wiggle',
    shake: 'animate-shake',
    flip: 'animate-flip',
    zoomIn: 'animate-zoom-in',
    zoomOut: 'animate-zoom-out',
    blurIn: 'animate-blur-in',
    glow: 'animate-glow',
    gradient: 'animate-gradient-x',
    shimmer: 'animate-shimmer',
    wave: 'animate-wave',
    morphing: 'animate-morphing',
    neonPulse: 'animate-neon-pulse'
  };

  let classes = baseClasses[type] || '';

  // Add delay classes
  if (options.delay) {
    const delayClass = `animate-entrance-delay-${Math.min(options.delay, 5)}`;
    classes += ` ${delayClass}`;
  }

  // Add duration classes
  if (options.duration) {
    const durationClasses = {
      fast: 'duration-200',
      normal: 'duration-300',
      slow: 'duration-500',
      slower: 'duration-700',
      slowest: 'duration-1000'
    };
    classes += ` ${durationClasses[options.duration] || 'duration-300'}`;
  }

  // Add easing classes
  if (options.easing) {
    const easingClasses = {
      linear: 'ease-linear',
      in: 'ease-in',
      out: 'ease-out',
      inOut: 'ease-in-out'
    };
    classes += ` ${easingClasses[options.easing] || 'ease-out'}`;
  }

  return classes.trim();
};

// Performance monitoring for animations
export const animationPerformance = {
  start: (name) => {
    if (typeof performance !== 'undefined' && performance.mark) {
      performance.mark(`animation-${name}-start`);
    }
  },
  end: (name) => {
    if (typeof performance !== 'undefined' && performance.mark && performance.measure) {
      performance.mark(`animation-${name}-end`);
      performance.measure(`animation-${name}`, `animation-${name}-start`, `animation-${name}-end`);
    }
  },
  getMetrics: (name) => {
    if (typeof performance !== 'undefined' && performance.getEntriesByName) {
      return performance.getEntriesByName(`animation-${name}`);
    }
    return [];
  }
};

// Check if user prefers reduced motion
export const prefersReducedMotion = () => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
  return false;
};

// Responsive animation based on screen size
export const getResponsiveAnimation = (animations) => {
  if (typeof window === 'undefined') return animations.default;

  const width = window.innerWidth;
  
  if (width < 640) return animations.mobile || animations.default;
  if (width < 768) return animations.tablet || animations.default;
  if (width < 1024) return animations.laptop || animations.default;
  return animations.desktop || animations.default;
};

// Animation queue system
export class AnimationQueue {
  constructor() {
    this.queue = [];
    this.isRunning = false;
  }

  add(animation) {
    this.queue.push(animation);
    if (!this.isRunning) {
      this.run();
    }
  }

  async run() {
    this.isRunning = true;
    
    while (this.queue.length > 0) {
      const animation = this.queue.shift();
      await animation();
    }
    
    this.isRunning = false;
  }

  clear() {
    this.queue = [];
    this.isRunning = false;
  }
}