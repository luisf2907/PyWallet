// filepath: i:\Github\pywallet3\frontend-react\src\hooks\useDeviceType.js
import { useState, useEffect } from 'react';

const useDeviceType = () => {
  const [deviceType, setDeviceType] = useState('desktop');

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) { // Mobile breakpoint
        setDeviceType('mobile');
      } else { // Desktop
        setDeviceType('desktop');
      }
    };

    handleResize(); // Set initial device type
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return deviceType;
};

export default useDeviceType;
