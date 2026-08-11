const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'src');

// Map of old absolute paths to new absolute paths
const moveMap = new Map();

// Helper to add moves
function planMove(oldRelPath, newRelPath) {
    const oldAbs = path.join(srcDir, oldRelPath);
    const newAbs = path.join(srcDir, newRelPath);
    if (fs.existsSync(oldAbs)) {
        moveMap.set(oldAbs, newAbs);
    }
}

// 1. Plan moves for existing screens
const features = ['analytics', 'assistant', 'auth', 'calendar', 'home', 'notifications', 'onboarding', 'profile', 'reminders', 'schedule'];
features.forEach(feature => {
    const featureDir = path.join(srcDir, 'features', feature);
    if (fs.existsSync(featureDir)) {
        const files = fs.readdirSync(featureDir);
        files.forEach(file => {
            if (file.endsWith('.tsx') || file.endsWith('.ts')) {
                planMove(`features/${feature}/${file}`, `features/${feature}/screens/${file}`);
            }
        });
    }
});

// 2. Plan moves for components
const componentMoves = {
    'chat': 'assistant/components',
    'dashboard': 'home/components',
    'profile': 'profile/components',
    'schedule': 'schedule/components'
};
Object.entries(componentMoves).forEach(([oldCompFolder, newFeatureCompFolder]) => {
    const oldDir = path.join(srcDir, 'components', oldCompFolder);
    if (fs.existsSync(oldDir)) {
        const files = fs.readdirSync(oldDir);
        files.forEach(file => {
            planMove(`components/${oldCompFolder}/${file}`, `features/${newFeatureCompFolder}/${file}`);
        });
    }
});

// 3. Plan moves for stores
const storeMoves = {
    'chatStore.ts': 'assistant/store/chatStore.ts',
    'onboardingStore.ts': 'onboarding/store/onboardingStore.ts'
};
Object.entries(storeMoves).forEach(([oldFile, newPath]) => {
    planMove(`store/${oldFile}`, `features/${newPath}`);
});


// Helper to resolve an import path
function resolveImport(currentFilePath, importStr) {
    const currentDir = path.dirname(currentFilePath);
    const absPath = path.resolve(currentDir, importStr);
    
    // Check if it exists with extensions
    const exts = ['.tsx', '.ts', '.js', '/index.ts', '/index.tsx'];
    for (const ext of [''].concat(exts)) {
        if (fs.existsSync(absPath + ext)) {
            return absPath + ext;
        }
    }
    
    // Check in moveMap (if it's not on disk yet)
    for (const oldAbs of moveMap.keys()) {
        const oldAbsNoExt = oldAbs.replace(/\.tsx?$/, '');
        if (absPath === oldAbsNoExt || absPath === oldAbs) {
            return oldAbs;
        }
    }
    
    return null; // Could not resolve locally (might be node_module)
}

function processFiles() {
    // Collect all source files
    const allFiles = [];
    function walk(dir) {
        if (!fs.existsSync(dir)) return;
        const items = fs.readdirSync(dir);
        items.forEach(item => {
            const p = path.join(dir, item);
            const stat = fs.statSync(p);
            if (stat.isDirectory()) {
                walk(p);
            } else if (p.endsWith('.ts') || p.endsWith('.tsx')) {
                allFiles.push(p);
            }
        });
    }
    walk(srcDir);

    // Add files that are about to be moved (if not already found)
    for (const oldPath of moveMap.keys()) {
        if (!allFiles.includes(oldPath)) {
            allFiles.push(oldPath);
        }
    }

    const modifiedContents = new Map();

    allFiles.forEach(file => {
        let content = fs.readFileSync(file, 'utf8');
        let changed = false;

        // Current path of this file (after move, if it moves)
        const fileNewPath = moveMap.get(file) || file;
        const fileOldPath = file;

        // Match imports and exports
        const importRegex = /(?:import|export)\s+.*?(?:from\s+)?['"](\.[^'"]+)['"]/g;
        
        let match;
        const replacements = [];
        while ((match = importRegex.exec(content)) !== null) {
            const importStr = match[1];
            
            // Resolve using OLD path because the text is currently written relative to the old path
            let resolvedTargetOldAbs = resolveImport(fileOldPath, importStr);
            
            if (resolvedTargetOldAbs) {
                // If the target is moving, get its new path. Otherwise, it stays where it is.
                const targetNewAbs = moveMap.get(resolvedTargetOldAbs) || resolvedTargetOldAbs;
                
                // Calculate new relative import
                let newRel = path.relative(path.dirname(fileNewPath), targetNewAbs).replace(/\\/g, '/');
                
                // Remove extension
                newRel = newRel.replace(/\.tsx?$/, '');
                
                if (!newRel.startsWith('.')) {
                    newRel = './' + newRel;
                }
                
                if (newRel !== importStr) {
                    replacements.push({
                        start: match.index,
                        end: match.index + match[0].length,
                        oldImport: importStr,
                        newImport: newRel,
                        fullMatch: match[0]
                    });
                }
            }
        }

        if (replacements.length > 0) {
            // Apply replacements backwards to not mess up indices
            for (let i = replacements.length - 1; i >= 0; i--) {
                const r = replacements[i];
                const newFullStr = r.fullMatch.replace(r.oldImport, r.newImport);
                content = content.substring(0, r.start) + newFullStr + content.substring(r.end);
            }
            changed = true;
        }

        if (changed) {
            modifiedContents.set(fileOldPath, content);
        }
    });

    // Execute moves and write files
    // First create all target directories
    for (const newPath of moveMap.values()) {
        fs.mkdirSync(path.dirname(newPath), { recursive: true });
    }

    // Now move files
    for (const [oldPath, newPath] of moveMap.entries()) {
        if (oldPath !== newPath) {
            fs.renameSync(oldPath, newPath);
        }
    }

    // Write modified contents to their new locations
    for (const [oldPath, content] of modifiedContents.entries()) {
        const newPath = moveMap.get(oldPath) || oldPath;
        fs.writeFileSync(newPath, content, 'utf8');
    }
    
    // Clean up empty old directories
    Object.entries(componentMoves).forEach(([oldCompFolder]) => {
        const oldDir = path.join(srcDir, 'components', oldCompFolder);
        if (fs.existsSync(oldDir) && fs.readdirSync(oldDir).length === 0) {
            fs.rmdirSync(oldDir);
        }
    });

    console.log(`Moved ${moveMap.size} files and updated imports in ${modifiedContents.size} files.`);
}

processFiles();
