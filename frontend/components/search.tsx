import React, { useState } from 'react';
import FolderStructure from './folderstructure';
import { Input, Button } from '@nextui-org/react';

interface Item {
    name: string;
    type: string;
    contents?: Item[];
}

const Search = ({ data }: { data: Item[] }) => {
    const [inputValue, setInputValue] = useState(''); // add state for the input value
    const [selectedFile, setSelectedFile] = useState(''); // add state for the selected file
    const [path, setPath] = useState('');

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(event.target.value); // update the input value when the input changes
    };

    const handleButtonClick = async () => {
        // Check if a file has been selected and an input value has been entered
        if (!selectedFile || !inputValue) {
            console.error('A file must be selected and a query must be entered before sending a request');
            return;
        }

        // Get the URL of the selected file
        let repo = localStorage.getItem('repo-link');
        const response = await fetch('http://127.0.0.1:5000/get_file_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                repo_url: repo,
                file_path: path,
            }),
        });

        if (!response.ok) {
            console.error('Failed to get the file URL');
            return;
        }

        const data = await response.json();
        const fileUrl = data.file_url;
        const searchResponse = await fetch('http://127.0.0.1:5000/ask_code_llm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                codeurl: fileUrl,
                query: inputValue,
            }),
        });

        if (!searchResponse.ok) {
            console.error('Search request failed');
            return;
        }

        const searchData = await searchResponse.json();
        console.log(searchData);
    };

    const handleFileSelect = async (filePath: string, fileName: string) => {
        setSelectedFile(fileName); // update the selected file when a file is clicked
        let fullpath = filePath + '/' + fileName;
        setPath(fullpath);
    };

    return (
        <div className="flex flex-row h-[82vh]">
            <div className="custom-scrollbar w-[26%] p-5 overflow-y-auto">
                <FolderStructure data={data} onFileSelect={handleFileSelect} />
            </div>
            <div className="flex flex-col w-[75%] justify-end">
                <div className="w-full p-10 flex items-center">
                    <div className="w-[30%] border-2 border-purple-500 rounded-l-xl p-[0.36rem] flex items-center justify-center text-purple-500">{selectedFile}</div>
                    <Input type="email" variant="bordered" radius='none' value={inputValue} onChange={handleInputChange} />
                    <Button color="primary" variant="bordered" radius='none' className="rounded-r-xl" onClick={handleButtonClick}>
                        Send
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default Search;
