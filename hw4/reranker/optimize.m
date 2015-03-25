clear all
close all


%% gradient descent
resolution = 2;
range = -3:3;
n = length(range)^3;
[o_x,o_y,o_z] = meshgrid(range,range,range);
offset = [reshape(o_x,n,1) reshape(o_y,n,1) reshape(o_z,n,1)]*resolution;

theta_seed = [-5.625 -3.125 -7.125];

biggest = 0;
prev_biggest = 0;
term_flag = false;
changed_res = false;
num_bytes = 0;
max_iter = 5;
iter = 1;
bad_operation = false;
while ~term_flag && iter <= max_iter && ~bad_operation
    % generate new parameters
    theta = bsxfun(@plus,theta_seed,offset);
    bleu_score = zeros(size(theta,1),1);
    
    % calculate BLEU score for each set of parameters
    num_bytes = 0;
    for i = 1:length(bleu_score)
        fprintf(repmat('\b',1,num_bytes))
        num_bytes = fprintf('iteration %d of %d',i,length(bleu_score));
        cmd = ['./rerank -l ' num2str(theta(i,1))...
            ' -t ' num2str(theta(i,2))...
            ' -s ' num2str(theta(i,3))...
            '| ./compute-bleu'];
        [status, score] = system(cmd);
        if status
            bad_operation = true;
        end
        bleu_score(i) = str2double(score);
    end
    fprintf('\n')
    % find the best calculated score
    [val,idx] = max(bleu_score);
    
    % move the seed theta to the one with the best BLEU score or change the
    % resolution if the best BLEU score is given by the same seed
    if val ~= biggest
        theta_seed = theta(idx,:);
        prev_biggest = biggest;
        biggest = val;
        fprintf('Bigger score found. Shifting...\n')
        iter = 1;
    else
        resolution = resolution*0.5;
        [o_x,o_y,o_z] = meshgrid(range,range,range);
        offset = [reshape(o_x,n,1) reshape(o_y,n,1) reshape(o_z,n,1)]*resolution;
        changed_res = true;
        fprintf('Same score found. changing resolution...\n')
        iter = iter+1;
    end
    
    %fprintf(repmat('\b',1,num_bytes));
    fprintf('previous score: %6.6f | score: %6.6f | delta score: %6.6f | iteration: %d | max iter: %d\n',...
        prev_biggest*100, biggest*100, (biggest-prev_biggest)*100, iter, max_iter);
    if abs(prev_biggest - biggest) < 1e-8 && ~changed_res
        term_flag = true;
    end
    if changed_res
        changed_res = false;
    end
end
if val > biggest
    biggest = val;
end
theta(idx,:)
fprintf('\n')