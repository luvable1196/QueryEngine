import { useState, useEffect, useRef, useCallback } from 'react';

// Hook for intersection observer animations
export const useIntersectionObserver = (options = {}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const elementRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated) {
          setIsVisible(true);
          setHasAnimated(true);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => {
      if (elementRef.current) {
        observer.unobserve(elementRef.current);
      }
    };
  }, [hasAnimated, options]);

  return [elementRef, isVisible];
};

// // Hook for staggered animations
// export const useStaggeredAnimation = (items, delay = 100) => {
//   const [visibleItems, setVisibleItems] = useState(new Set());
//   const [elementRef, isVisible] = useIntersectionObserver();

//   useEffect(() => {
//     if (isVisible && items.length > 0) {
//       items.forEach((_, index) => {
//         setTimeout(() => {
//           setVisibleItems(prev => new Set([...prev, index]));
//         }, index * delay);
//       });
//     }
//   }, [isVisible, items, delay]);

//   return [elementRef, visibleItems];
// };


export const useStaggeredAnimation = (delay = 0.1) => {
  return {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6, delay }
  };
};
// Custom hook for counter animations
export const useCounterAnimation = (targetValue, duration = 2) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime = null;
    const startValue = 0;
    
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / (duration * 1000), 1);
      
      // Easing function for smooth animation
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOut);
      
      setCount(currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [targetValue, duration]);
  
  return count;
};


// Hook for typing animation
export const useTypewriter = (text, speed = 50) => {
  const [displayText, setDisplayText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [isStarted, setIsStarted] = useState(false);

  const startTyping = useCallback(() => {
    if (!isStarted && text) {
      setIsStarted(true);
      let currentIndex = 0;
      
      const timer = setInterval(() => {
        if (currentIndex < text.length) {
          setDisplayText(text.slice(0, currentIndex + 1));
          currentIndex++;
        } else {
          clearInterval(timer);
          setIsComplete(true);
        }
      }, speed);

      return () => clearInterval(timer);
    }
  }, [text, speed, isStarted]);

  const reset = useCallback(() => {
    setDisplayText('');
    setIsComplete(false);
    setIsStarted(false);
  }, []);

  return { displayText, isComplete, startTyping, reset };
};

// Hook for number counting animation
export const useCountAnimation = (targetValue, duration = 2000, startOnVisible = true) => {
  const [count, setCount] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [elementRef, isVisible] = useIntersectionObserver();

  useEffect(() => {
    if ((startOnVisible && isVisible) || (!startOnVisible && !isAnimating)) {
      setIsAnimating(true);
      const startTime = Date.now();
      const startValue = count;
      const difference = targetValue - startValue;

      const updateCount = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = Math.round(startValue + difference * easeOutQuart);
        
        setCount(currentValue);

        if (progress < 1) {
          requestAnimationFrame(updateCount);
        } else {
          setIsAnimating(false);
        }
      };

      requestAnimationFrame(updateCount);
    }
  }, [targetValue, duration, startOnVisible, isVisible, isAnimating, count]);

  return [elementRef, count, isAnimating];
};

// Hook for scroll-based animations
export const useScrollAnimation = () => {
  const [scrollY, setScrollY] = useState(0);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      const progress = Math.min(currentScrollY / maxScroll, 1);
      
      setScrollY(currentScrollY);
      setScrollProgress(progress);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return { scrollY, scrollProgress };
};

// Hook for mouse position tracking
export   const useMousePosition = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: e.clientX,
        y: e.clientY
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return mousePosition;
};

// Hook for loading states with skeleton animation
export const useLoadingState = (initialLoading = false) => {
  const [isLoading, setIsLoading] = useState(initialLoading);
  const [loadingProgress, setLoadingProgress] = useState(0);

  const startLoading = useCallback(() => {
    setIsLoading(true);
    setLoadingProgress(0);
  }, []);

  const updateProgress = useCallback((progress) => {
    setLoadingProgress(Math.min(Math.max(progress, 0), 100));
  }, []);

  const finishLoading = useCallback(() => {
    setLoadingProgress(100);
    setTimeout(() => {
      setIsLoading(false);
      setLoadingProgress(0);
    }, 300);
  }, []);

  return {
    isLoading,
    loadingProgress,
    startLoading,
    updateProgress,
    finishLoading
  };
};

// Hook for card flip animation
export const useFlipCard = () => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const flip = useCallback(() => {
    if (!isAnimating) {
      setIsAnimating(true);
      setIsFlipped(prev => !prev);
      setTimeout(() => setIsAnimating(false), 600);
    }
  }, [isAnimating]);

  return { isFlipped, isAnimating, flip };
};

// Hook for hover effects
export const useHoverAnimation = () => {
  const [isHovered, setIsHovered] = useState(false);
  const elementRef = useRef(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const handleMouseEnter = () => setIsHovered(true);
    const handleMouseLeave = () => setIsHovered(false);

    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter);
      element.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return [elementRef, isHovered];
};

// Hook for page transitions
export const usePageTransition = () => {
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitionDirection, setTransitionDirection] = useState('forward');

  const startTransition = useCallback((direction = 'forward') => {
    setTransitionDirection(direction);
    setIsTransitioning(true);
  }, []);

  const endTransition = useCallback(() => {
    setTimeout(() => setIsTransitioning(false), 500);
  }, []);

  return {
    isTransitioning,
    transitionDirection,
    startTransition,
    endTransition
  };
};

// Hook for element size tracking
export const useElementSize = () => {
  const [size, setSize] = useState({ width: 0, height: 0 });
  const elementRef = useRef(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setSize({ width, height });
      }
    });

    resizeObserver.observe(element);

    return () => {
      resizeObserver.unobserve(element);
    };
  }, []);

  return [elementRef, size];
};

// Hook for shake animation (for errors)
export const useShakeAnimation = () => {
  const [isShaking, setIsShaking] = useState(false);
  const elementRef = useRef(null);

  const shake = useCallback(() => {
    setIsShaking(true);
    setTimeout(() => setIsShaking(false), 820);
  }, []);

  return [elementRef, isShaking, shake];
};

// Hook for pulse animation (for notifications)
export const usePulseAnimation = () => {
  const [isPulsing, setIsPulsing] = useState(false);

  const pulse = useCallback(() => {
    setIsPulsing(true);
    setTimeout(() => setIsPulsing(false), 1000);
  }, []);

  const startPulse = useCallback(() => setIsPulsing(true), []);
  const stopPulse = useCallback(() => setIsPulsing(false), []);

  return { isPulsing, pulse, startPulse, stopPulse };
};

// Hook for morphing blob animation
export const useMorphingBlob = () => {
  const [morphingStyle, setMorphingStyle] = useState({});
  const [isAnimating, setIsAnimating] = useState(false);

  const startMorphing = useCallback(() => {
    setIsAnimating(true);
    setMorphingStyle({
      animation: 'morphing 8s ease-in-out infinite',
    });
  }, []);

  const stopMorphing = useCallback(() => {
    setIsAnimating(false);
    setMorphingStyle({});
  }, []);

  return { morphingStyle, isAnimating, startMorphing, stopMorphing };
};