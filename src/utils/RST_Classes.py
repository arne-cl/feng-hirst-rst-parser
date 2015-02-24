
class2rel = {
'Attribution': ['attribution', 'attribution-e', 'attribution-n', 'attribution-negative'],
'Background' : ['background', 'background-e', 'circumstance', 'circumstance-e'],
'Cause' : ['cause', 'cause-result', 'result', 'result-e', 'consequence', 'consequence-n-e', 'consequence-n', 'consequence-s-e', 'consequence-s'],
'Comparison' : ['comparison', 'comparison-e', 'preference',  'preference-e', 'analogy','analogy-e', 'proportion'],
'Condition' : ['condition', 'condition-e', 'hypothetical', 'contingency', 'otherwise'],
'Contrast' : ['contrast', 'concession', 'concession-e', 'antithesis', 'antithesis-e'],
'Elaboration' : ['elaboration-additional', 'elaboration-additional-e', 'elaboration-general-specific-e', 'elaboration-general-specific', 'elaboration-part-whole', 'elaboration-part-whole-e', 'elaboration-process-step', 'elaboration-process-step-e', 'elaboration-object-attribute-e', 'elaboration-object-attribute', 'elaboration-set-member', 'elaboration-set-member-e', 'example', 'example-e', 'definition', 'definition-e'],
'Enablement' : ['purpose', 'purpose-e', 'enablement', 'enablement-e'],
'Evaluation' : ['evaluation', 'evaluation-n', 'evaluation-s-e', 'evaluation-s', 'interpretation-n', 'interpretation-s-e', 'interpretation-s', 'interpretation', 'conclusion', 'comment', 'comment-e', 'comment-topic'],
'Explanation' : ['evidence', 'evidence-e', 'explanation-argumentative', 'explanation-argumentative-e', 'reason', 'reason-e'],
'Joint' : ['list', 'disjunction'],
'Manner-Means' : ['manner', 'manner-e', 'means', 'means-e'],
'Topic-Comment' : ['problem-solution', 'problem-solution-n', 'problem-solution-s', 'question-answer', 'question-answer-n', 'question-answer-s',  'statement-response', 'statement-response-n', 'statement-response-s', 'topic-comment', 'comment-topic', 'rhetorical-question'],
'Summary' : ['summary', 'summary-n', 'summary-s', 'restatement', 'restatement-e'],
'Temporal' : ['temporal-before', 'temporal-before-e', 'temporal-after', 'temporal-after-e', 'temporal-same-time', 'temporal-same-time-e', 'sequence', 'inverted-sequence'],
'Topic-Change' : ['topic-shift', 'topic-drift'],
'textual-organization' : ['textualorganization'],
'span' : ['span'],
'same-unit' : ['same-unit']
}

rel_status_classes = []
for rel in class2rel:
    rel_status_classes.append(rel + '[N][S]')
    rel_status_classes.append(rel + '[N][N]')
    rel_status_classes.append(rel + '[S][N]')
    
rel2class = {}
for cl in class2rel:
    rel2class[cl.lower()] = cl
    for rel in class2rel[cl]:
        rel2class[rel] = cl
