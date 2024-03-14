'use client';
import React, { useState, ChangeEvent } from 'react';
import { Card, CardBody, Input } from '@nextui-org/react';
import { Button } from '@nextui-org/button';
import FolderStructure from '../../components/folderstructure'; // import your FolderStructure component

export default function App() {
  const [inputValue, setInputValue] = useState('');
  const [data, setData] = useState(null); // add a state variable for the response data

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handleButtonClick = async () => {
    const response = await fetch('http://127.0.0.1:5000/get_structure_clean', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ key: inputValue })
    });

    if (!response.ok) {
      console.error('HTTP error', response.status);
    } else {
      const data = await response.json();
      setData(data.clean); 
    }
  };

  if (data) {
    return <FolderStructure data={data} />;
  }

  return (
    <div className="flex flex-col items-center justify-center md:pt-10 md:mt-40 ">
      <Card className="w-[80%]">
        <CardBody>
          <Input size="lg" type="text" label="GitHub URL" value={inputValue} onChange={handleInputChange} />
          <Button size="lg" className="mt-4" color="primary" variant="bordered" onClick={handleButtonClick}>Next</Button>
        </CardBody>
      </Card>
    </div>
  );
}