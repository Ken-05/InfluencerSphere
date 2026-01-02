/**
 * AlertBanner.tsx
 * ---------------
 * Displays system alerts (new influencer updates, API failures, etc.)
 */

import React from "react";

interface Props {
  message: string;
  type?: "success" | "error" | "info";
}

const AlertBanner: React.FC<Props> = ({ message, type = "info" }) => {
  const bgColor =
    type === "success" ? "bg-green-200" :
    type === "error" ? "bg-red-200" : "bg-blue-200";

  return (
    <div className={`${bgColor} p-3 rounded my-2`}>
      {message}
    </div>
  );
};

export default AlertBanner;
