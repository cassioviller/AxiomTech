import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Function to check if element is in viewport
export function isInViewport(element: HTMLElement): boolean {
  const rect = element.getBoundingClientRect();
  return (
    rect.top <= (window.innerHeight || document.documentElement.clientHeight) - 150 &&
    rect.bottom >= 0
  );
}

// Function to handle smooth scroll to an element
export function scrollToElement(elementId: string): void {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  const header = document.querySelector('header');
  const headerHeight = header?.offsetHeight || 0;
  const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
  const offsetPosition = elementPosition - headerHeight;
  
  window.scrollTo({
    top: offsetPosition,
    behavior: 'smooth'
  });
}

// Function to format form data
export function formatFormData(formData: FormData): Record<string, string> {
  const formObject: Record<string, string> = {};
  
  formData.forEach((value, key) => {
    formObject[key] = value.toString();
  });
  
  return formObject;
}
