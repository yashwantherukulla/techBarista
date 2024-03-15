'use client';
import React, { useState, useEffect, useRef } from "react";
import { Input, Button } from "@nextui-org/react";
import ReactMarkdown from "react-markdown";

interface Item {
  name: string;
  type: string;
  contents?: Item[];
}

interface ChatItem {
  type: "question" | "response";
  content: string;
}

const Instant = ({ data }: { data: Item[] }) => {
  const [inputValue, setInputValue] = useState(""); // add state for the input value
  const [currentQuestion, setCurrentQuestion] = useState("First question");
  const [currentResponse, setCurrentResponse] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatItem[]>([]); // add state for the chat history

  const handleResponseChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentResponse(event.target.value);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value); // update the input value when the input changes
  };

  const handleResponseSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Add the response to the chat history
    setChatHistory((prevChatHistory) => [
      ...prevChatHistory,
      { type: "response", content: currentResponse },
    ]);

    // Make a POST request to the API with the response
    const apiResponse = await fetch("http://your-api-url", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        response: currentResponse,
      }),
    });

    const data = await apiResponse.json();
    setCurrentQuestion(data.newQuestion);
    setCurrentResponse("");
  };

  // ...

  return (
    <div className="flex flex-col h-[82vh] justify-between">
      <div className="flex flex-row">
        <div className="flex flex-col w-[90%] justify-end ml-4">
          <div className="flex flex-col custom-scrollbar w-full p-5 overflow-y-auto">
            {chatHistory.map((item, index) => {
              if (item.type === "question") {
                return (
                  <div
                    key={index}
                    className="p-2 rounded-lg my-1 border-2 border-blue-700 bg-blue-200 bg-opacity-25 text-blue-200 inline-block mr-auto"
                    style={{
                      overflowWrap: "break-word",
                      wordBreak: "break-word",
                    }}
                  >
                    <ReactMarkdown>{item.content}</ReactMarkdown>
                  </div>
                );
              } else {
                return (
                  <div
                    key={index}
                    className="p-2 rounded-lg my-1 border-2 border-green-700 bg-opacity-25 bg-green-200 text-green-200 inline-block ml-auto w-[95%]"
                    style={{
                      overflowWrap: "break-word",
                      wordBreak: "break-word",
                    }}
                  >
                    <ReactMarkdown>{item.content}</ReactMarkdown>
                  </div>
                );
              }
            })}
          </div>
          <div className="w-full p-10 flex items-center">
            <Input
              type="text"
              variant="bordered"
              radius="none"
              value={inputValue}
              onChange={handleInputChange}
            />
            <Button
              color="primary"
              radius="none"
              style={{
                backgroundColor: "rgba(59, 130, 246, 0.3)",
                border: "2px solid rgb(59,130,246)",
                color: "rgb(59,130,246)",
                fontWeight: "bold",
              }}
              className="rounded-r-xl"
              onClick={handleButtonClick}
            >
              Send
            </Button>
          </div>
        </div>
      </div>
      <div className="w-full p-10 flex items-center">
        <h2>{currentQuestion}</h2>
        <form
          onSubmit={handleResponseSubmit}
          className="w-full flex items-center"
        >
          <Input
            type="text"
            variant="bordered"
            radius="none"
            value={currentResponse}
            onChange={handleResponseChange}
            className="flex-grow"
          />
          <Button
            color="primary"
            radius="none"
            style={{
              backgroundColor: "rgba(59, 130, 246, 0.3)",
              border: "2px solid rgb(59,130,246)",
              color: "rgb(59,130,246)",
              fontWeight: "bold",
            }}
            className="rounded-r-xl"
            type="submit"
          >
            Submit
          </Button>
        </form>
      </div>
    </div>
  );
};

export default Instant;
