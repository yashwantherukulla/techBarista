import React, { useState } from 'react';
import { AiFillFolder, AiFillFile } from "react-icons/ai";
import { MdKeyboardArrowRight, MdKeyboardArrowDown } from "react-icons/md";

interface Item {
    name: string;
    type: string;
    contents?: Item[];
}

const FolderStructure = ({ data, onFileSelect, path = '' }: { data: Item[], onFileSelect: (filePath: string, fileName: string) => void, path?: string }) => {
    const [openFolders, setOpenFolders] = useState<string[]>([]);

    const handleClick = (name: string) => {
        setOpenFolders(prev => {
            if (prev.includes(name)) {
                return prev.filter(folder => folder !== name);
            } else {
                return [...prev, name];
            }
        });
    };

    const handleFileClick = (name: string) => {
        onFileSelect(path, name); // call the callback function with the file path and name
    };

    return (
        <ul className="list-none pl-3">
            {data.map((item, index) => (
                <li key={index} className="mt-1">
                    {item.type === 'dir' ? (
                        <div className="flex items-center" onClick={() => handleClick(item.name)}>
                            {openFolders.includes(item.name) ? <MdKeyboardArrowDown /> : <MdKeyboardArrowRight />}
                            <AiFillFolder className="ml-2" /> {item.name}
                        </div>
                    ) : (
                        <div className="flex items-center pl-6">
                            <AiFillFile className="ml-[0.09rem]" /> <span onClick={() => handleFileClick(item.name)} className='cursor-pointer'>{item.name}</span>
                        </div>
                    )}
                    {item.type === 'dir' && openFolders.includes(item.name) && item.contents && (
                        <FolderStructure data={item.contents} onFileSelect={onFileSelect} path={path + '/' + item.name} />
                    )}
                </li>
            ))}
        </ul>
    );
};

export default FolderStructure;