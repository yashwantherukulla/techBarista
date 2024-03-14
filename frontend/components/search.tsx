import React, { useState } from 'react'
import FolderStructure from './folderstructure'; 
import { Input } from '@nextui-org/react';

interface Item {
    name: string;
    type: string;
    contents?: Item[];
}

const Search = ({ data }: { data: Item[] }) => {
    const [inputValue, setInputValue] = useState(''); // add state for the input value

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(event.target.value); // update the input value when the input changes
    };

    return (
        <div className='flex flex-row'>
            <div className='custom-scrollbar w-[26%] p-5 overflow-y-auto max-h-[82vh]'>
                <FolderStructure data={data} /> 
            </div>
            <div className='w-[70%]'>
                <Input type="email" variant="bordered" value={inputValue} onChange={handleInputChange} />
            </div>
        </div>
    )
}

export default Search