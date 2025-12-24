import { Check } from 'lucide-react';
import { motion } from 'framer-motion';

interface Step {
  label: string;
  completed: boolean;
}

interface ProgressStepperProps {
  steps: Step[];
  currentStep: number;
}

const ProgressStepper = ({ steps, currentStep }: ProgressStepperProps) => {
  return (
    <div className="flex items-center justify-between max-w-3xl mx-auto">
      {steps.map((step, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber === currentStep;
        const isCompleted = step.completed;

        return (
          <div key={index} className="flex items-center flex-1">
            <div className="flex flex-col items-center flex-1">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: isActive ? 1.1 : 1 }}
                className={`w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all ${
                  isCompleted
                    ? 'bg-green-500 text-white'
                    : isActive
                    ? 'bg-gradient-to-r from-purple-600 to-fuchsia-600 text-white shadow-lg shadow-purple-500/50'
                    : 'bg-white/10 text-gray-400'
                }`}
              >
                {isCompleted ? <Check size={24} /> : stepNumber}
              </motion.div>
              <p
                className={`mt-2 text-sm font-semibold ${
                  isActive ? 'text-purple-400' : 'text-gray-400'
                }`}
              >
                {step.label}
              </p>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`flex-1 h-1 mx-2 rounded transition-all ${
                  step.completed
                    ? 'bg-gradient-to-r from-purple-500 to-fuchsia-500'
                    : 'bg-white/10'
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default ProgressStepper;
