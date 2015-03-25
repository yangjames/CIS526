clear all
close all

%% gradient descent
resolution = 0.05;
range = -5:0.1:0;
n = size(range,2)^3;
[o_x,o_y,o_z] = meshgrid(range,range,range);

theta = [reshape(o_x,n,1) reshape(o_y,n,1) reshape(o_z,n,1)]*resolution;

bleu_score = zeros(size(theta,1),1);
num_bytes = 0;
for i = 1:length(bleu_score)
    fprintf(repmat('\b',1,num_bytes));
    num_bytes = fprintf('progress: %3.6f%%',(i/n)*100);
    cmd = ['./rerank -l ' num2str(theta(i,1))...
            ' -t ' num2str(theta(i,2)) ' -s ' num2str(theta(i,3)) '| ./compute-bleu'];
    [status, score] = system(cmd);
    if status
        break
    end
    bleu_score(i) = str2double(score);
end
    
% find the best calculated score
[val,idx] = max(bleu_score);
num_bytes = fprintf('score: %6.6f\n', biggest*100);
theta(idx,:)
fprintf('\n')