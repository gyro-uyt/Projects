def lcs(X, Y):
    m = len(X)
    n = len(Y)
    
    L = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])
                
    return L

def get_diff(old_lines, new_lines):
    L = lcs(old_lines, new_lines)
    
    m = len(old_lines)
    n = len(new_lines)
    
    diff = []
    i = m
    j = n
    
    while i > 0 and j > 0:
        if old_lines[i-1] == new_lines[j-1]:
            diff.append(('equal', old_lines[i-1]))
            i -= 1
            j -= 1
        elif L[i-1][j] > L[i][j-1]:
            diff.append(('delete', old_lines[i-1]))
            i -= 1
        else:
            diff.append(('insert', new_lines[j-1]))
            j -= 1
            
    while i > 0:
        diff.append(('delete', old_lines[i-1]))
        i -= 1
    while j > 0:
        diff.append(('insert', new_lines[j-1]))
        j -= 1
        
    diff.reverse()
    return diff

def get_side_by_side_diff(old_lines, new_lines):
    diff = get_diff(old_lines, new_lines)
    sbs = []
    
    i = 0
    left_line_num = 1
    right_line_num = 1
    
    while i < len(diff):
        op, line = diff[i]
        
        if op == 'equal':
            sbs.append({
                'type': 'equal', 
                'left': line, 'left_num': left_line_num,
                'right': line, 'right_num': right_line_num
            })
            left_line_num += 1
            right_line_num += 1
            i += 1
        elif op == 'delete':
            # See if the very next one is an insert, treating it as a replacement on same visual row
            if i + 1 < len(diff) and diff[i+1][0] == 'insert':
                sbs.append({
                    'type': 'replace',
                    'left': line, 'left_num': left_line_num,
                    'right': diff[i+1][1], 'right_num': right_line_num
                })
                left_line_num += 1
                right_line_num += 1
                i += 2
            else:
                sbs.append({
                    'type': 'delete',
                    'left': line, 'left_num': left_line_num,
                    'right': '', 'right_num': ''
                })
                left_line_num += 1
                i += 1
        elif op == 'insert':
            sbs.append({
                'type': 'insert',
                'left': '', 'left_num': '',
                'right': line, 'right_num': right_line_num
            })
            right_line_num += 1
            i += 1
            
    return sbs

def get_chunks(base_lines, new_lines):
    diff = get_diff(base_lines, new_lines)
    chunks = []
    base_idx = 0
    current_chunk = None
    
    for op, line in diff:
        if op == 'equal':
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = None
            base_idx += 1
        elif op == 'delete':
            if not current_chunk:
                current_chunk = {'base_start': base_idx, 'base_end': base_idx + 1, 'lines': []}
            else:
                current_chunk['base_end'] += 1
            base_idx += 1
        elif op == 'insert':
            if not current_chunk:
                current_chunk = {'base_start': base_idx, 'base_end': base_idx, 'lines': [line]}
            else:
                current_chunk['lines'].append(line)
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def basic_merge(base_content, mine_content, theirs_content):
    """
    True 3-way block merge leveraging Dynamic Programming differences.
    """
    if mine_content == theirs_content: return mine_content, False
    if mine_content == base_content: return theirs_content, False
    if theirs_content == base_content: return mine_content, False

    base_lines = base_content.splitlines()
    mine_lines = mine_content.splitlines()
    theirs_lines = theirs_content.splitlines()
    
    mine_chunks = get_chunks(base_lines, mine_lines)
    theirs_chunks = get_chunks(base_lines, theirs_lines)
    
    for c in mine_chunks: c['source'] = 'mine'
    for c in theirs_chunks: c['source'] = 'theirs'
    
    all_chunks = mine_chunks + theirs_chunks
    all_chunks.sort(key=lambda x: x['base_start'])
    
    def overlap(a, b):
        if max(a['base_start'], b['base_start']) < min(a['base_end'], b['base_end']): return True
        if a['base_start'] == b['base_start'] and a['base_end'] == b['base_end'] and a['base_start'] == a['base_end']: return True
        return False

    has_conflict = False
    merged_lines = []
    last_base_idx = 0
    
    i = 0
    while i < len(all_chunks):
        c = all_chunks[i]
        
        conflict_group = [c]
        j = i + 1
        while j < len(all_chunks):
            if any(overlap(all_chunks[j], x) for x in conflict_group):
                conflict_group.append(all_chunks[j])
                j += 1
            else:
                break
                
        sources = set(x['source'] for x in conflict_group)
        is_conflict = False
        
        if len(sources) > 1:
            if len(conflict_group) == 2 and \
               conflict_group[0]['lines'] == conflict_group[1]['lines'] and \
               conflict_group[0]['base_start'] == conflict_group[1]['base_start'] and \
               conflict_group[0]['base_end'] == conflict_group[1]['base_end']:
                conflict_group = [conflict_group[0]]
            else:
                is_conflict = True
                
        group_start = min(x['base_start'] for x in conflict_group)
        group_end = max(x['base_end'] for x in conflict_group)
        
        while last_base_idx < group_start:
            merged_lines.append(base_lines[last_base_idx])
            last_base_idx += 1
            
        if is_conflict:
            has_conflict = True
            break
        else:
            for ch in conflict_group:
                merged_lines.extend(ch['lines'])
            last_base_idx = group_end
            
        i = j

    if has_conflict:
        merged = f"<<<<<<< CURRENT VERSION\n{mine_content}\n=======\n{theirs_content}\n>>>>>>> INCOMING VERSION"
        return merged, True
        
    while last_base_idx < len(base_lines):
        merged_lines.append(base_lines[last_base_idx])
        last_base_idx += 1
        
    return '\n'.join(merged_lines), False
