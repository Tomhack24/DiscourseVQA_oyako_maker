import json
from collections import defaultdict

# Load child_parent data
child_parent_data = {}
with open('child_parent.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        video_id = data['video_id']
        # Create a mapping from child to parent for this video
        child_to_parent = {}
        for relation in data['child_parent']:
            child_to_parent[relation['child']] = relation['parent']
        child_parent_data[video_id] = child_to_parent

# Load QA data and analyze
results = []
with open('QA_DATASET_GEMINI_W_STRUCTURE.jsonl', 'r') as f:
    for line in f:
        qa = json.loads(line)
        qa_number = qa['QA_number']
        video_id = qa['video_id']
        evidence = qa['Evidence']
        
        if video_id not in child_parent_data:
            print(f"Warning: video_id {video_id} not found in child_parent data")
            continue
        
        child_to_parent = child_parent_data[video_id]
        
        # Get all parents of evidence items
        parents = []
        for child in evidence:
            if child in child_to_parent:
                parent = child_to_parent[child]
                parents.append(parent)
            else:
                # If no parent mapping exists, the item might be a root
                # Check if the child is itself a parent in the structure
                parents.append(child)
        
        # Count how many parents (with duplicates) are in the evidence
        parents_in_evidence_count = sum(1 for p in parents if p in evidence)
        unique_parents = set(parents)
        parents_in_evidence = [p for p in unique_parents if p in evidence]
        
        # Calculate ratio (count each parent occurrence separately)
        if len(parents) > 0:
            ratio = parents_in_evidence_count / len(parents)
        else:
            ratio = 0.0
        
        result = {
            'QA_number': qa_number,
            'video_id': video_id,
            'evidence': evidence,
            'parents': parents,
            'unique_parents': list(unique_parents),
            'parents_in_evidence': parents_in_evidence,
            'num_parents': len(parents),
            'num_parents_in_evidence_count': parents_in_evidence_count,
            'num_unique_parents': len(unique_parents),
            'num_unique_parents_in_evidence': len(parents_in_evidence),
            'ratio': ratio
        }
        results.append(result)
        
        print(f"QA {qa_number} (video {video_id}):")
        print(f"  Evidence: {evidence}")
        print(f"  Parents: {parents}")
        print(f"  Unique parents: {list(unique_parents)}")
        print(f"  Parents in evidence: {parents_in_evidence}")
        print(f"  Ratio: {ratio:.2%} ({parents_in_evidence_count}/{len(parents)})")
        print()

# Calculate average ratio
if results:
    average_ratio = sum(r['ratio'] for r in results) / len(results)
    print("=" * 60)
    print(f"Average ratio of parents in evidence: {average_ratio:.2%}")
    print(f"Total QA analyzed: {len(results)}")
    print("=" * 60)

# Save detailed results to file
with open('parent_coverage_analysis.jsonl', 'w') as f:
    for result in results:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')

print("\nDetailed results saved to: parent_coverage_analysis.jsonl")
